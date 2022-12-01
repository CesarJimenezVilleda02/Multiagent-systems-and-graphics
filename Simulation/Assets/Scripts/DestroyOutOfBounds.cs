using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Class used to destroy zombies and humans when they are aout of bounds.
/// </summary>
public class DestroyOutOfBounds : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (transform.position.x > 800)
        {
            Destroy(this.gameObject);
        }    
    }
}
