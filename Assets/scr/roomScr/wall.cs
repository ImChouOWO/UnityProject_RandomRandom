using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class wall : MonoBehaviour
{
    
    public GameObject[] walls;
    public room Room;
    
    void Start()
    {
        if (Room.rightCheck  && !Room.leftCheck && !Room.upCheck && !Room.downCheck)
        {
            Instantiate(walls[0],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (!Room.rightCheck  && !Room.leftCheck && Room.upCheck  && !Room.downCheck)
        {
            Instantiate(walls[1],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (!Room.rightCheck  && Room.leftCheck  && !Room.upCheck && !Room.downCheck)
        {
            Instantiate(walls[2],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (!Room.rightCheck  && !Room.leftCheck && !Room.upCheck && Room.downCheck )
        {
            Instantiate(walls[3],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (Room.rightCheck  && Room.leftCheck  && !Room.upCheck && !Room.downCheck)
        {
            Instantiate(walls[4],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (!Room.rightCheck  && !Room.leftCheck && Room.upCheck  && Room.downCheck )
        {
            Instantiate(walls[5],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (Room.rightCheck  && !Room.leftCheck && Room.upCheck  && !Room.downCheck)
        {
            Instantiate(walls[6],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (Room.rightCheck  && !Room.leftCheck && !Room.upCheck && Room.downCheck )
        {
            Instantiate(walls[7],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (!Room.rightCheck  && Room.leftCheck  && !Room.upCheck && Room.downCheck )
        {
            Instantiate(walls[8],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (!Room.rightCheck  && Room.leftCheck  && Room.upCheck  && !Room.downCheck)
        {
            Instantiate(walls[9],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (Room.rightCheck  && !Room.leftCheck && Room.upCheck  && Room.downCheck )
        {
            Instantiate(walls[10],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (Room.rightCheck  && Room.leftCheck  && !Room.upCheck && Room.downCheck )
        {
            Instantiate(walls[11],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (!Room.rightCheck  && Room.leftCheck  && Room.upCheck  && Room.downCheck )
        {
            Instantiate(walls[12],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (Room.rightCheck  && Room.leftCheck  && Room.upCheck  && !Room.downCheck)
        {
            Instantiate(walls[13],Room.gameObject.transform.position,Quaternion.identity);
        }
        if (Room.rightCheck  && Room.leftCheck  && Room.upCheck  && Room.downCheck )
        {
            Instantiate(walls[14],Room.gameObject.transform.position,Quaternion.identity);
        }
        
    }
}
