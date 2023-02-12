using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;


public class generator : MonoBehaviour
{
    [Header("房間infor")]
    
    public GameObject prefab;
    public int roomQty;
    public LayerMask roomMask;
    public Color startRoomcolor,endRoomcolor;
    private GameObject endRoom;
    [Header("座標infor")]
    public Transform pointPos;
    public float xOffSet;
    public float yOffset;
    
    public List<room> rooms = new List<room>();
    //這是定義一個 List<room> 類型的變數 rooms，它是一個用來存放 room 類型物件的動態陣列。
    // List<T> 是 C# 中提供的泛型類型，可以存放任何符合類型的物件。
    // 在這個範例中，rooms 可以存放多個 room 類型的物件。new List<room>() 表示創建了一個新的 room 類型的 List。
    
    public enum Direction
    {

        up,
        down,
        left,
        right
    }
    public Direction direction;
    void Start()
    {




       for (int i = 0; i < roomQty; i++)
       {
        rooms.Add(Instantiate(prefab,pointPos.position,Quaternion.identity).GetComponent<room>());
        //建立物件，並由GetComponent<room>()獲取room.cs下的參數
        changePos();
        
        
       } 
        //rooms[0].GetComponent<SpriteRenderer>().color = startRoomcolor;


        endRoom = rooms[0].gameObject;//將room型別的參數轉換為gameobject
        foreach (var room in rooms)
        {
            
            if (room.transform.position.sqrMagnitude > endRoom.transform.position.sqrMagnitude)
            {
                endRoom = room.gameObject;
                
            }
            setUpRoom(room,room.transform.position);
        }
        
        //endRoom.GetComponent<SpriteRenderer>().color = endRoomcolor;
        endRoomCheck(endRoom.GetComponent<room>(),endRoom.gameObject.transform.position);
        
        setUpRoom(endRoom.GetComponent<room>(),endRoom.gameObject.transform.position);
        
        
        
    
    

       
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.R))
        {
            SceneManager.LoadScene(SceneManager.GetActiveScene().name);
        }
        
    }
    public void changePos(){
        direction = (Direction)Random.Range(0,4);
    do
    {
        switch (direction)
        {
            case Direction.up:
                pointPos.position += new Vector3(0,yOffset,0);
                
                break;
            case Direction.down:
                pointPos.position -= new Vector3(0,yOffset,0);
                break;
            case Direction.left:
                pointPos.position -= new Vector3(xOffSet,0,0);
                break;
            case Direction.right:
                pointPos.position += new Vector3(xOffSet,0,0);
                break;

        }

    } while (Physics2D.OverlapCircle(pointPos.position,0.2f,roomMask));
        

    }
    public void setUpRoom(room newDoor,Vector3 roomPos){
        
        newDoor.upCheck = Physics2D.OverlapCircle(roomPos + new Vector3(0,yOffset,0),0.2f,roomMask);
        newDoor.downCheck =Physics2D.OverlapCircle(roomPos - new Vector3(0,yOffset,0),0.2f,roomMask);
        newDoor.leftCheck = Physics2D.OverlapCircle(roomPos - new Vector3(xOffSet,0,0),0.2f,roomMask);
        newDoor.rightCheck =Physics2D.OverlapCircle(roomPos + new Vector3(xOffSet,0,0),0.2f,roomMask);
    }
    public void endRoomCheck(room newEndRoom,Vector3 finalRoomPos){
        Debug.Log(finalRoomPos);
        newEndRoom.isEndRoom = true;
        direction = (Direction)Random.Range(0,4);
        if (!newEndRoom.upCheck)
        {
            finalRoomPos += new Vector3(0,yOffset,0);
            rooms.Add(Instantiate(prefab,finalRoomPos,Quaternion.identity).GetComponent<room>());
            rooms[rooms.Count-1].downCheck = true;
            return;
        }
        else if (!newEndRoom.downCheck)
        {
            finalRoomPos -= new Vector3(0,yOffset,0);
            rooms.Add(Instantiate(prefab,finalRoomPos,Quaternion.identity).GetComponent<room>());
            rooms[rooms.Count-1].upCheck = true;
            return;
        }
        else if (!newEndRoom.leftCheck)
        {
            finalRoomPos -= new Vector3(xOffSet,0,0);
            rooms.Add(Instantiate(prefab,finalRoomPos,Quaternion.identity).GetComponent<room>());
            rooms[rooms.Count-1].rightCheck = true;
            return;
        }
        else if (!newEndRoom.rightCheck)
        {
            finalRoomPos += new Vector3(xOffSet,0,0);
            rooms.Add(Instantiate(prefab,finalRoomPos,Quaternion.identity).GetComponent<room>());
            rooms[rooms.Count-1].leftCheck = true;
            return;
        }
    }
}   
