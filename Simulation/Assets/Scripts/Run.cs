using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Class used to make zombies run forward in the highway.
/// </summary>
public class Run : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
         transform.Translate(Vector3.forward * Time.deltaTime * 5);
    }
}
