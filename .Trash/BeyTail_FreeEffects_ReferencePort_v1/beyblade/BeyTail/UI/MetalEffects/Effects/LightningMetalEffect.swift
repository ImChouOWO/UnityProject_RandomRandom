import UIKit

/// Dynamic-color lightning trail based on the supplied reference video.
///
/// Visual structure:
/// - one thin angular bolt
/// - a soft color-matched outer glow
/// - a bright near-white electrical core
/// - short transient branches controlled by the global particle profile
final class LightningMetalEffect: MetalEffect {
    private struct BoltNode {
        let x: Float
        let y: Float
        let alpha: Float
        let color: UIColor
    }

    private var program: MetalProgramID = 0
    private var positionLocation: MetalLocation = -1
    private var colorLocation: MetalLocation = -1

    private var time: Float = 0

    private let segmentFloats = MetalFloatBuffer(
        capacity: 256 * 2 * 6
    )

    private let branchFloats = MetalFloatBuffer(
        capacity: 96 * 2 * 6
    )

    override func onMetalReady(
        context: MetalRenderContext
    ) {
        program = MetalHelper.makeProgram(
            .flatColor
        )

        positionLocation = metalGetAttribLocation(
            program,
            "aPosition"
        )

        colorLocation = metalGetAttribLocation(
            program,
            "aColor"
        )
    }

    override func draw(
        trackData: MetalTrackData,
        context: MetalRenderContext,
        effectType: EffectType
    ) {
        guard effectType == .lightning else {
            reset()
            return
        }

        time += (1.0 / 30.0) * context.dtScale

        metalUseProgram(program)

        for (trackID, points) in trackData
        where points.count >= 2 {
            let nodes = makeNodes(
                points,
                trackID: trackID,
                context: context
            )

            guard nodes.count >= 2 else {
                continue
            }

            drawMainBolt(
                nodes,
                widthMultiplier:
                    effectType.trailWidthMultiplier
            )

            drawBranches(
                nodes,
                trackID: trackID,
                context: context,
                widthMultiplier:
                    effectType.trailWidthMultiplier
            )
        }
    }

    override func reset() {
        time = 0
        segmentFloats.clear()
        branchFloats.clear()
    }

    private func makeNodes(
        _ points: [MetalTrailSample],
        trackID: Int,
        context: MetalRenderContext
    ) -> [BoltNode] {
        let lastIndex = points.count - 1
        let sampleStride = Self.nodeStride

        var sourceIndices = Array(
            Swift.stride(
                from: 0,
                through: lastIndex,
                by: sampleStride
            )
        )

        if sourceIndices.last != lastIndex {
            sourceIndices.append(lastIndex)
        }

        let clipPerPixel =
            FreeEffectRenderSupport.clipPerPixel(
                context: context
            )

        let timeStep = floor(
            time * Self.flickerStepsPerSecond
        )

        var output: [BoltNode] = []
        output.reserveCapacity(sourceIndices.count)

        for (nodeIndex, sourceIndex) in
            sourceIndices.enumerated() {
            let sample = points[sourceIndex]
            var position =
                FreeEffectRenderSupport.clipPosition(
                    sample.first,
                    context: context
                )

            let previousIndex = max(
                sourceIndex - sampleStride,
                0
            )

            let nextIndex = min(
                sourceIndex + sampleStride,
                lastIndex
            )

            let previous =
                FreeEffectRenderSupport.clipPosition(
                    points[previousIndex].first,
                    context: context
                )

            let next =
                FreeEffectRenderSupport.clipPosition(
                    points[nextIndex].first,
                    context: context
                )

            let normal =
                FreeEffectRenderSupport.segmentNormal(
                    x0: previous.0,
                    y0: previous.1,
                    x1: next.0,
                    y1: next.1
                )

            let progress =
                sourceIndices.count > 1
                ? Float(nodeIndex)
                    / Float(sourceIndices.count - 1)
                : 1

            let endpointEnvelope =
                sin(.pi * progress)

            let randomSeed =
                Float(trackID) * 31.7
                + Float(sourceIndex) * 7.13
                + timeStep * 11.9

            let jitterPixels =
                Self.jitterPixels
                * context.particleSizeMultiplier
                * endpointEnvelope
                * FreeEffectRenderSupport.signedHash(
                    randomSeed
                )

            position.0 +=
                normal.0
                * jitterPixels
                * clipPerPixel

            position.1 +=
                normal.1
                * jitterPixels
                * clipPerPixel

            output.append(
                BoltNode(
                    x: position.0,
                    y: position.1,
                    alpha: sample.second,
                    color: sample.first.color
                )
            )
        }

        return output
    }

    private func drawMainBolt(
        _ nodes: [BoltNode],
        widthMultiplier: Float
    ) {
        metalBlendFunc(
            MGL_SRC_ALPHA,
            MGL_ONE
        )

        drawSegments(
            nodes,
            lineWidth:
                Self.glowWidthPixels
                * widthMultiplier,
            whiteMix: 0.08,
            alphaScale: 0.20
        )

        drawSegments(
            nodes,
            lineWidth:
                Self.coreWidthPixels
                * widthMultiplier,
            whiteMix: 0.72,
            alphaScale: 0.92
        )

        metalBlendFunc(
            MGL_SRC_ALPHA,
            MGL_ONE_MINUS_SRC_ALPHA
        )
    }

    private func drawSegments(
        _ nodes: [BoltNode],
        lineWidth: Float,
        whiteMix: Float,
        alphaScale: Float
    ) {
        segmentFloats.clear()

        for index in 1..<nodes.count {
            let first = nodes[index - 1]
            let second = nodes[index]

            let firstColor =
                FreeEffectRenderSupport.mixedColor(
                    first.color,
                    whiteMix: whiteMix,
                    alpha:
                        first.alpha
                        * alphaScale
                )

            let secondColor =
                FreeEffectRenderSupport.mixedColor(
                    second.color,
                    whiteMix: whiteMix,
                    alpha:
                        second.alpha
                        * alphaScale
                )

            FreeEffectRenderSupport.appendLineVertex(
                to: segmentFloats,
                x: first.x,
                y: first.y,
                color: firstColor
            )

            FreeEffectRenderSupport.appendLineVertex(
                to: segmentFloats,
                x: second.x,
                y: second.y,
                color: secondColor
            )
        }

        let vertexCount =
            (nodes.count - 1) * 2

        guard vertexCount > 0 else {
            return
        }

        metalLineWidth(
            max(lineWidth, 1)
        )

        MetalHelper.drawInterleaved(
            buffer: segmentFloats,
            strideBytes: Self.bytesPerVertex,
            attributes: Self.lineAttributes(
                positionLocation:
                    positionLocation,
                colorLocation:
                    colorLocation
            ),
            mode: MGL_LINES,
            vertexCount: vertexCount
        )
    }

    private func drawBranches(
        _ nodes: [BoltNode],
        trackID: Int,
        context: MetalRenderContext,
        widthMultiplier: Float
    ) {
        guard nodes.count >= 4,
              context.particleFrequencyMultiplier > 0 else {
            return
        }

        branchFloats.clear()

        let timeStep = floor(
            time * Self.branchStepsPerSecond
        )

        let probability = min(
            Self.branchProbability
            * context.particleFrequencyMultiplier,
            0.45
        )

        let clipPerPixel =
            FreeEffectRenderSupport.clipPerPixel(
                context: context
            )

        var branchCount = 0

        for index in 1..<(nodes.count - 1) {
            let seed =
                Float(trackID) * 17.3
                + Float(index) * 29.1
                + timeStep * 13.7

            guard FreeEffectRenderSupport.hash(seed)
                    < probability else {
                continue
            }

            let previous = nodes[index - 1]
            let current = nodes[index]
            let next = nodes[index + 1]

            let tangentX =
                next.x - previous.x

            let tangentY =
                next.y - previous.y

            let tangentLength = max(
                sqrt(
                    tangentX * tangentX
                    + tangentY * tangentY
                ),
                0.000_001
            )

            let tx = tangentX / tangentLength
            let ty = tangentY / tangentLength
            let nx = -ty
            let ny = tx

            let side: Float =
                FreeEffectRenderSupport.hash(
                    seed + 4.7
                ) > 0.5
                ? 1
                : -1

            let branchPixels =
                (
                    Self.branchLengthPixels
                    * (
                        0.65
                        + FreeEffectRenderSupport.hash(
                            seed + 9.4
                        ) * 0.55
                    )
                )
                * context.particleSizeMultiplier

            let directionX =
                nx * side
                - tx * 0.35

            let directionY =
                ny * side
                - ty * 0.35

            let endX =
                current.x
                + directionX
                * branchPixels
                * clipPerPixel

            let endY =
                current.y
                + directionY
                * branchPixels
                * clipPerPixel

            let startColor =
                FreeEffectRenderSupport.mixedColor(
                    current.color,
                    whiteMix: 0.60,
                    alpha:
                        current.alpha * 0.70
                )

            let endColor =
                FreeEffectRenderSupport.mixedColor(
                    current.color,
                    whiteMix: 0.82,
                    alpha: 0
                )

            FreeEffectRenderSupport.appendLineVertex(
                to: branchFloats,
                x: current.x,
                y: current.y,
                color: startColor
            )

            FreeEffectRenderSupport.appendLineVertex(
                to: branchFloats,
                x: endX,
                y: endY,
                color: endColor
            )

            branchCount += 1

            if branchCount >= Self.maximumBranches {
                break
            }
        }

        guard branchCount > 0 else {
            return
        }

        metalLineWidth(
            max(
                Self.branchWidthPixels
                * widthMultiplier,
                1
            )
        )

        MetalHelper.drawInterleaved(
            buffer: branchFloats,
            strideBytes: Self.bytesPerVertex,
            attributes: Self.lineAttributes(
                positionLocation:
                    positionLocation,
                colorLocation:
                    colorLocation
            ),
            mode: MGL_LINES,
            vertexCount: branchCount * 2
        )
    }

    private static func lineAttributes(
        positionLocation: MetalLocation,
        colorLocation: MetalLocation
    ) -> [MetalVertexAttribute] {
        [
            MetalVertexAttribute(
                location: positionLocation,
                size: 2,
                offsetBytes: 0
            ),
            MetalVertexAttribute(
                location: colorLocation,
                size: 4,
                offsetBytes: 8
            )
        ]
    }

    private static let bytesPerVertex = 24
    private static let nodeStride = 3

    private static let jitterPixels: Float = 2.1
    private static let flickerStepsPerSecond: Float = 15
    private static let branchStepsPerSecond: Float = 9

    private static let glowWidthPixels: Float = 3.2
    private static let coreWidthPixels: Float = 0.75

    private static let branchProbability: Float = 0.065
    private static let branchLengthPixels: Float = 8
    private static let branchWidthPixels: Float = 0.55
    private static let maximumBranches = 8
}
