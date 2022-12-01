using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Class used to generate the highway the cars will traverse.
/// </summary>
public class GenerateHighway : MonoBehaviour
{
    public GameObject highwayPrefab;
    public Vector3 currHighwayLocation;
    public Vector3 offsetHighway;
    public int highWayLength;

    // Start is called before the first frame update
    void Start()
    {
        for(int i = 0; i < highWayLength; i++)
        {
            Instantiate(highwayPrefab, currHighwayLocation, highwayPrefab.transform.rotation);
            currHighwayLocation += offsetHighway;
        }
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
