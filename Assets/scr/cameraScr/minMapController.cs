using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class minMapController : MonoBehaviour
{
    public GameObject minMap;
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Tab))
        {
            minMap.SetActive(true);
        }
        else if (Input.GetKeyUp(KeyCode.Tab))
        {
            minMap.SetActive(false);
        }
    }
}
