using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Class used to contorl the cars and their movements.
/// </summary>
public class CarManager : MonoBehaviour
{
    float timePassed = 0;
    bool broken = false;
    bool hasTornado = false;

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        timePassed += Time.deltaTime;
        if(timePassed > 10.0f && !broken)
        {
            Destroy(this.gameObject);
        }
    }

    /// <summary>
    /// Create a smoke effect when a car breaks and move the main camera to a spectating position.
    /// </summary>
    /// <param name="camera"></param>
    /// <param name="tornado"></param>
    /// <param name="speed"></param>
    public void Break(GameObject camera, GameObject tornado, int speed)
    {
        if(!broken)
        {
            broken = true;
            return;
        }
        if (speed == 0 && hasTornado == false)
        {
            hasTornado = true;
            camera.transform.position = new Vector3(transform.position.x, 75, transform.position.y);
            Instantiate(tornado, transform.position, tornado.transform.rotation);
        }
    }

    /// <summary>
    /// Start moving the car to a new position through an interval of time.
    /// </summary>
    /// <param name="timeToMove"></param>
    /// <param name="targetPos"></param>
    /// <returns></returns>
    public IEnumerator MoveCar(float timeToMove, Vector3 targetPos)
    {
        timePassed = 0.0f;
        Vector3 currentPos = transform.position;

        float timeElapsed = 0;

        while (timeElapsed < timeToMove)
        {
            transform.position = Vector3.Lerp(currentPos, targetPos, timeElapsed / timeToMove);
            timeElapsed += Time.deltaTime;
            yield return null;
        }
    }
}
