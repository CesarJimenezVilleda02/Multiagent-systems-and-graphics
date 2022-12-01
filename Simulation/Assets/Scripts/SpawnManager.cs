using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Class used to spawn zombies in the game.
/// </summary>
public class SpawnManager : MonoBehaviour
{
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

    /// <summary>
    /// Generate a new zombie at the left of the highway.
    /// </summary>
    void GenerateZombieLeft()
    {
        Vector3 position = new Vector3(spawnPos, 0, Random.Range(startZombieRangeLeft, endZombieRangeLeft));
        Instantiate(zombie, position, zombie.transform.rotation);
    }

    /// <summary>
    /// Generate a new zombie at the right of the highway.
    /// </summary>
    void GenerateZombieRight()
    {
        Vector3 position = new Vector3(spawnPos, 0, Random.Range(startZombieRangeRight, endZombieRangeRight));
        Instantiate(zombie, position, zombie.transform.rotation);
    }
}
