using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CarManager : MonoBehaviour
{
    public Vector3 speed;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
         transform.Translate(speed * Time.deltaTime);
    }

    void ChangeSpeed(Vector3 newSpeed) 
    {
        speed = newSpeed;
    }

    void Accelerate(Vector3 acceleration) 
    {
        speed += acceleration;
    }
}
