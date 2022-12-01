using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TrafficManager : MonoBehaviour
{
    // Car variables
    private int[] lanes = { 16, 0, -16 };
    public float distanceMultiplier = 30.0f;
    public Dictionary<int, GameObject> cars = new Dictionary<int, GameObject>();
    public GameObject car;
    public GameObject camera;

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {

    }

    public void UpdateCars(CJsonResponse response, float timePerStep)
    {
        // Update all cars according to state
        foreach (CAgent car in response.data)
        {
            if (car.state != "SPAWN")
            {
                // CALCULATE NEXT POSITION
                Vector3 targetPos = new Vector3(car.x * distanceMultiplier, 0, lanes[car.z]);
                // Start moving process
                CarManager manager = GetCar(car.id);
                StartCoroutine(manager.MoveCar(timePerStep, targetPos));
                if(car.state == "BREAK")
                {
                    manager.Break(camera);
                }
            }
            else if (car.state == "SPAWN" && !cars.ContainsKey(car.id))
            {
                CreateCar(car);
            }
        }
    }

    public void CreateCar(CAgent agent)
    {
        Vector3 position = new Vector3(0, 0, lanes[agent.z]);
        GameObject newCar = (GameObject)Instantiate(car, position, car.transform.rotation);
        newCar.name = "Car_Agent_" + agent.id.ToString();
        cars.Add(agent.id, newCar);
    }

    public CarManager GetCar(int car)
    {
        string car_name = "Car_Agent_" + car.ToString();
        GameObject selectedCar = GameObject.Find(car_name);
        CarManager manager = selectedCar.GetComponent<CarManager>();
        return manager;
    }
}
