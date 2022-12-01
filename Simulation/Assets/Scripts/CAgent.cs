using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Class used to model the information needed for each car.
/// </summary>
[System.Serializable]
public class CAgent
{
    public int id;
    public int speed;
    public string state;
    public int x;
    public int z;
}