using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Class used to deserialize the response from the python server.
/// </summary>
[System.Serializable]
public class CJsonResponse
{
    public List<CAgent> data;

    public string ToString()
    {
        string result = "";

        foreach (CAgent car in data)
        {
            result += " " + car.state + ",";
        }

        return result;
    }
}