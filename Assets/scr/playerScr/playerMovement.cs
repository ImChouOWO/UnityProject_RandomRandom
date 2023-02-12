using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class playerMovement : MonoBehaviour
{
    public GameObject player;
    public Rigidbody2D rigidbody2d;
    public float speed = 10f;
    public Vector2 movement;
    public Animator ani;
    private AnimatorStateInfo animStateInfo;
    public float playerSize;
   
  
    void Start()
    {
        rigidbody2d = GetComponent<Rigidbody2D>();
        ani = GetComponent<Animator>();
       
        transform.localScale = new Vector3(playerSize,playerSize, 1);
    

    }

    // Update is called once per frame
    void Update()
    {
        movement.x = Input.GetAxisRaw("Horizontal");
        movement.y = Input.GetAxisRaw("Vertical");
        animStateInfo = ani.GetCurrentAnimatorStateInfo(0);
        AnimationSwitch();
        IsAttack();
        isflip();
        
        
        
        

    }
    private void FixedUpdate() {
        rigidbody2d.MovePosition(rigidbody2d.position += movement*speed*Time.fixedDeltaTime);
        // MovePosition是用來直接變更物件的移動
        

       
        
    }
    void IsAttack() {
        
        if (!animStateInfo.IsName("playerAttack_2") && Input.GetKeyDown(KeyCode.J))
        {

            ani.SetTrigger("isAttack");
            
            

        }
        if (animStateInfo.IsName("playerAttack_1") && Input.GetKeyDown(KeyCode.J)&& animStateInfo.normalizedTime > 0.4f)
        {
            ani.SetTrigger("isAttack2");
        }
        


    }
    void AnimationSwitch() {
        
        ani.SetFloat("isWalk",movement.magnitude);
        

    }
    void isflip() {
        if (movement.x != 0)
        {
            transform.localScale = new Vector3(movement.x*playerSize,1* playerSize, 1);
        }
        
    }
   
    
}
