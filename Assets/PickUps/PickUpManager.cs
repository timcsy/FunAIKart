using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

/// <summary>
/// The class that communicates between Item and Car group
/// </summary>
public class PickUpManager : MonoBehaviour
{
    // Singleton
    public static PickUpManager instance;

    [Header("UI")]
    [SerializeField]
    private Image wheelBar;
    [SerializeField]
    private Image gasBar;

    [Header("General Stats")]
    [Tooltip("The point at which Speed should slow down (Default: 0.5)")]
    [SerializeField] private float SlowThreshold;
    [Tooltip("The speed at which below SlowThreshold run at (Default: 0.75)")]
    [SerializeField] private float SlowRatio;

    [Header("Wheel Stats")]
    [Tooltip("Maxium Amount of Wheel (Default: 40.0)")]
    [SerializeField] private float MaxWheel;
    [Tooltip("The amount each Pick Up gives (Default: 15.0)")]
    [SerializeField] private float WheelPickUpAmount;
    [Tooltip("The Rate at which Wheel degrades (Default: 2.0)")]
    [SerializeField] private float WheelConsumeRate;

    [Header("Gas Stats")]
    [Tooltip("Maxium Amount of Gas (Default: 40.0)")]
    [SerializeField] private float MaxGas;
    [Tooltip("The amount each Pick Up gives (Default: 15.0)")]
    [SerializeField] private float GasPickUpAmount;
    [Tooltip("The Rate at which Gas consumes (Default: 2.0)")]
    [SerializeField] private float GasConsumeRate;

    private int currentID;
    private List<GameObject> ListOfCar;
    private List<CarStats> ListOfCarStats;

    public enum PickUpType { Wheel , Gas }

    void Awake()
    {
        instance = this;
        currentID = 0;
           
        ListOfCarStats = new List<CarStats>();
    }

    void Start()
    {
        ListOfCar = new List<GameObject>(GameObject.FindGameObjectsWithTag("Player"));
        foreach (GameObject c in ListOfCar)
            RegisterCar(c.GetComponent<KartGame.KartSystems.ArcadeKart>());
    }

    private void RegisterCar(KartGame.KartSystems.ArcadeKart kart)
    {
        kart.MyID = currentID;
        currentID++;
        ListOfCarStats.Add(new CarStats(MaxWheel, MaxGas));
    }

    public void PickUp(PickUpType pickUpType, int ID)
    {
        switch (pickUpType)
        {
            case PickUpType.Wheel:
                ListOfCarStats[ID].CurrentWheel += WheelPickUpAmount;
                if (ListOfCarStats[ID].CurrentWheel > MaxWheel)
                    ListOfCarStats[ID].CurrentWheel = MaxWheel;
                break;
            case PickUpType.Gas:
                ListOfCarStats[ID].CurrentGas += GasPickUpAmount;
                if (ListOfCarStats[ID].CurrentGas > MaxGas)
                    ListOfCarStats[ID].CurrentGas = MaxGas;
                break;
        }
    }

    void Update()
    {
        for (int i = 0; i < currentID; i++)
        {
            float speedMod = 1.0f;

            if (ListOfCar[i].GetComponent<Rigidbody>().velocity.sqrMagnitude > 0.1f)
                ListOfCarStats[i].CurrentGas -= GasConsumeRate * Time.deltaTime;
            if (ListOfCarStats[i].CurrentGas < MaxWheel * SlowThreshold)
                speedMod *= SlowRatio;

            if (ListOfCar[i].GetComponent<Rigidbody>().velocity.sqrMagnitude > 0.1f)
                ListOfCarStats[i].CurrentWheel -= WheelConsumeRate * Time.deltaTime;
            if (ListOfCarStats[i].CurrentWheel < MaxWheel * SlowThreshold)
                speedMod *= SlowRatio;

            ListOfCar[i].GetComponent<KartGame.KartSystems.ArcadeKart>().speedModifier = speedMod;
        }
        UpdateUI();
    }

    private void UpdateUI()
    {
        wheelBar.fillAmount = ListOfCarStats[0].CurrentWheel / MaxWheel;
        gasBar.fillAmount = ListOfCarStats[0].CurrentGas / MaxGas;
    }
}

class CarStats
{
    public float CurrentWheel;
    public float CurrentGas;

    public CarStats(float wheel, float gas)
    {
        CurrentWheel = wheel;
        CurrentGas = gas;
    }
}