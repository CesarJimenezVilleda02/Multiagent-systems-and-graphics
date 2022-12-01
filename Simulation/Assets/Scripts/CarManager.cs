using System.Collections;
using System.Collections.Generic;
using UnityEngine;

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
