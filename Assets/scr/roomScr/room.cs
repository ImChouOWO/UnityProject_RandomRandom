using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class room : MonoBehaviour
{
    public GameObject doorUp,doorDown,doorLeft,doorRight;
    public bool upCheck,downCheck,leftCheck,rightCheck,isEndRoom;
    void Start()
    {
        doorUp.SetActive(upCheck);
        doorDown.SetActive(downCheck);
        doorRight.SetActive(rightCheck);
        doorLeft.SetActive(leftCheck);
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    private void OnTriggerEnter2D(Collider2D collision)
    {
        
            
        if (collision.CompareTag("Player"))
        {
            cameraMovement.instance.chageTarget(transform);
            
        }
    }
}
