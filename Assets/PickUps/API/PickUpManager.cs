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
    [SerializeField]
    private Transform boostGrid;

    [Header("Prefab")]
    [SerializeField]
    private GameObject pfNitroUI;
    [SerializeField]
    private GameObject pfTurtleUI;

    [Header("General Stats")]
    [Tooltip("The point at which Speed should slow down (Default: 0.5)")]
    [SerializeField] private float SlowThreshold;
    [Tooltip("The speed at which below SlowThreshold run at (Default: 0.75)")]
    [SerializeField] private float SlowRatio;

    [Header("Wheel Stats")]
    [Tooltip("Maxium Amount of Wheel (Default: 50.0)")]
    [SerializeField] private float MaxWheel;
    [Tooltip("The amount each Pick Up gives (Default: 20.0)")]
    [SerializeField] private float WheelPickUpAmount;
    [Tooltip("The Rate at which Wheel degrades (Default: 1.0)")]
    [SerializeField] private float WheelConsumeRate;

    [Header("Gas Stats")]
    [Tooltip("Maxium Amount of Gas (Default: 50.0)")]
    [SerializeField] private float MaxGas;
    [Tooltip("The amount each Pick Up gives (Default: 20.0)")]
    [SerializeField] private float GasPickUpAmount;
    [Tooltip("The Rate at which Gas consumes (Default: 1.0)")]
    [SerializeField] private float GasConsumeRate;

    [Header("Nitro Stats")]
    [Tooltip("That amount of value increase for Acceleration (Default: 2.5)")]
    [SerializeField] private float AccelerationBoost;
    [Tooltip("That amount of value increase for Top Speed (Default: 5.0)")]
    [SerializeField] private float TopSpeedBoost;
    [Tooltip("The Duration of the Boost in Seconds (Default: 5.0)")]
    [SerializeField] private float NitroDuration;

    [Header("Turtle Stats")]
    [Tooltip("That amount of value decrease for Acceleration (Default: -5.0)")]
    [SerializeField] private float AccelerationDecrease;
    [Tooltip("That amount of value decrease for Top Speed (Default: -5.0)")]
    [SerializeField] private float TopSpeedDecrease;
    [Tooltip("The Duration of the decrease in Seconds (Default: 5.0)")]
    [SerializeField] private float TurtleDuration;

    private int currentID;
    private List<GameObject> ListOfCar;
    private List<CarStats> ListOfCarStats;

    public enum PickUpType { Wheel , Gas, Nitro, Turtle }

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
            case PickUpType.Nitro:
                ListOfCar[ID].GetComponent<KartGame.KartSystems.ArcadeKart>().AddPowerup(new KartGame.KartSystems.ArcadeKart.StatPowerup
                {
                    modifiers = new KartGame.KartSystems.ArcadeKart.Stats
                    {
                        Acceleration = AccelerationBoost,
                        TopSpeed = TopSpeedBoost
                    },
                    MaxTime = NitroDuration
                });
                GameObject pfN = Instantiate(pfNitroUI, boostGrid);
                pfN.GetComponent<BoostUI>().SetDuration(NitroDuration);
                break;
            case PickUpType.Turtle:
                ListOfCar[ID].GetComponent<KartGame.KartSystems.ArcadeKart>().AddPowerup(new KartGame.KartSystems.ArcadeKart.StatPowerup
                {
                    modifiers = new KartGame.KartSystems.ArcadeKart.Stats
                    {
                        Acceleration = AccelerationDecrease,
                        TopSpeed = TopSpeedDecrease
                    },
                    MaxTime = TurtleDuration
                });
                GameObject pfT = Instantiate(pfTurtleUI, boostGrid);
                pfT.GetComponent<BoostUI>().SetDuration(NitroDuration);
                break;
        }
    }

    void Update()
    {
        for (int i = 0; i < currentID; i++)
        {
            float speedMod = 1.0f;

            ListOfCarStats[i].CurrentGas -= (GasConsumeRate / 100.0f) * Time.deltaTime * ListOfCar[i].GetComponent<Rigidbody>().velocity.sqrMagnitude;
            if (ListOfCarStats[i].CurrentGas < MaxWheel * SlowThreshold)
                speedMod *= SlowRatio;

            ListOfCarStats[i].CurrentWheel -= (WheelConsumeRate / 100.0f) * Time.deltaTime * ListOfCar[i].GetComponent<Rigidbody>().velocity.sqrMagnitude;
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