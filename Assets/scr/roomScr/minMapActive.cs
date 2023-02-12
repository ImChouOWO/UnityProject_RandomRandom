using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class minMapActive : MonoBehaviour
{
    public GameObject mapObject;
    private void OnEnable()
    {
        mapObject = transform.parent.GetChild(0).gameObject;
        mapObject.SetActive(false);
    }
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    private void OnTriggerEnter2D(Collider2D collision)
    {
       
        if (collision.CompareTag("Player"))
        {
            mapObject.SetActive(true);
           
        }
    }
}
