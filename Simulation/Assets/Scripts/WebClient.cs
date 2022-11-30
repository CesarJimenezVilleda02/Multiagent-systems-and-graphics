// TC2008B Modelación de Sistemas Multiagentes con gráficas computacionales
// C# client to interact with Python server via POST
// Sergio Ruiz-Loza, Ph.D. March 2021

using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

public class WebClient : MonoBehaviour
{
    public GameObject trafficManager;
    public TrafficManager manager;
    public float timePerStep = 2.0f;
    public int max_steps = 200;
    public int curr_steps = 0;

    // IEnumerator - yield return
    IEnumerator SendData(string data)
    {
        while(curr_steps < max_steps)
        {

            WWWForm form = new WWWForm();
            form.AddField("bundle", "the data");
            string url = "http://localhost:8585";
            using (UnityWebRequest www = UnityWebRequest.Post(url, form))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(data);
                www.uploadHandler = (UploadHandler)new UploadHandlerRaw(bodyRaw);
                www.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
                //www.SetRequestHeader("Content-Type", "text/html");
                www.SetRequestHeader("Content-Type", "application/json");

                System.DateTime start = System.DateTime.Now;
                yield return www.SendWebRequest();          // Talk to Python
                if (www.isNetworkError || www.isHttpError)
                {
                    Debug.Log(www.error);
                }
                else
                {
                    Debug.Log(www.downloadHandler.text);    // Answer from Python
                    CJsonResponse state = JsonUtility.FromJson<CJsonResponse>(www.downloadHandler.text);
                    manager.UpdateCars(state, timePerStep);
                }
                System.DateTime end = System.DateTime.Now;
                System.TimeSpan elapsedTime = end - start;
                int seconds, milliseconds;
                seconds = elapsedTime.Seconds;
                milliseconds = elapsedTime.Milliseconds;
                float totalDuration = (float)seconds + ((float)milliseconds / 1000);
                yield return new WaitForSeconds(timePerStep - totalDuration);
            }
        }
    }


    // Start is called before the first frame update
    void Start()
    {
        string json = EditorJsonUtility.ToJson("{}");
        StartCoroutine(SendData(json));
        manager = trafficManager.GetComponent<TrafficManager>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}