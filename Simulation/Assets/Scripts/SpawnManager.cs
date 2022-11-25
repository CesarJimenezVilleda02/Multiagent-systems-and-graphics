using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Collections.Generic;

public class SpawnManager : MonoBehaviour
{
    public List<Vector3> lanes = new List<Vector3>(3);
    // Zombie spawning
    public GameObject zombie;
    public float startZombieRangeLeft;
    public float endZombieRangeLeft;
    public float startZombieRangeRight;
    public float endZombieRangeRight;
    public float spawnPos;
    private float startDelay = 2.0f;
    private float spawnInterval = 1.0f;

    // Start is called before the first frame update
    void Start()
    {
        InvokeRepeating("GenerateZombieLeft", startDelay, spawnInterval);
        InvokeRepeating("GenerateZombieRight", startDelay, spawnInterval);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void GenerateZombieLeft()
    {
        Vector3 position = new Vector3(spawnPos, 0, Random.Range(startZombieRangeLeft, endZombieRangeLeft));
        Instantiate(zombie, position, zombie.transform.rotation);
    }
    
    void GenerateZombieRight()
    {
        Vector3 position = new Vector3(spawnPos, 0, Random.Range(startZombieRangeRight, endZombieRangeRight));
        Instantiate(zombie, position, zombie.transform.rotation);
    }
}
