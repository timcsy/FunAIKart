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

    [SerializeField]
    private int PlayerID = 0;

    [SerializeField]
    private GameFlowManager flowManager;

    [Header("UI")]
    [SerializeField]
    private Image wheelBar;
    [SerializeField]
    private Image gasBar;
    [SerializeField]
    private Transform boostGrid;

    [Header("Prefab")]
    [SerializeField]
    private GameObject pfBoostUI;

    [Header("General Stats")]
    [Tooltip("The point at which Speed should slow down (Default: 0.5)")]
    [SerializeField] [Range(0.1f, 1.0f)] private float SlowThreshold;
    [Tooltip("The speed at which below SlowThreshold run at (Default: 0.75)")]
    [SerializeField] [Range(0.1f, 1.0f)] private float SlowRatio;

    [Header("Refill")]
    public RefillStats Wheel;
    public RefillStats Gas;

    [Header("Consumable")]
    public ConsumableStats Nitro;
    public ConsumableStats Turtle;
    public ConsumableStats Banana;

    private int currentID;
    private List<GameObject> ListOfCar;
    private List<CarStats> ListOfCarStats;

    public enum PickUpType { Wheel, Gas, Nitro, Turtle, Banana }

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
        ListOfCarStats.Add(new CarStats(Wheel.MaxAmount, Gas.MaxAmount));
    }

    public void PickUp(PickUpType pickUpType, int ID)
    {
        switch (pickUpType)
        {
            case PickUpType.Wheel:
                ListOfCarStats[ID].CurrentWheel += Wheel.PickUpAmount;
                if (ListOfCarStats[ID].CurrentWheel > Wheel.MaxAmount)
                    ListOfCarStats[ID].CurrentWheel = Wheel.MaxAmount;
                break;
            case PickUpType.Gas:
                ListOfCarStats[ID].CurrentGas += Gas.PickUpAmount;
                if (ListOfCarStats[ID].CurrentGas > Gas.MaxAmount)
                    ListOfCarStats[ID].CurrentGas = Gas.MaxAmount;
                break;
            case PickUpType.Nitro:
                ListOfCar[ID].GetComponent<KartGame.KartSystems.ArcadeKart>().AddPowerup(new KartGame.KartSystems.ArcadeKart.StatPowerup
                {
                    modifiers = new KartGame.KartSystems.ArcadeKart.Stats
                    {
                        Acceleration = Nitro.Values[0],
                        TopSpeed = Nitro.Values[1]
                    },
                    MaxTime = Nitro.Duration
                });
                GameObject pfN = Instantiate(pfBoostUI, boostGrid);
                pfN.GetComponent<BoostUI>().Initialize(Nitro.Duration, Color.cyan, "N");
                break;
            case PickUpType.Turtle:
                ListOfCar[ID].GetComponent<KartGame.KartSystems.ArcadeKart>().AddPowerup(new KartGame.KartSystems.ArcadeKart.StatPowerup
                {
                    modifiers = new KartGame.KartSystems.ArcadeKart.Stats
                    {
                        Acceleration = Turtle.Values[0],
                        TopSpeed = Turtle.Values[1]
                    },
                    MaxTime = Turtle.Duration
                });
                GameObject pfT = Instantiate(pfBoostUI, boostGrid);
                pfT.GetComponent<BoostUI>().Initialize(Turtle.Duration, Color.green, "T");
                break;
            case PickUpType.Banana:
                ListOfCar[ID].GetComponent<KartGame.KartSystems.ArcadeKart>().AddPowerup(new KartGame.KartSystems.ArcadeKart.StatPowerup
                {
                    modifiers = new KartGame.KartSystems.ArcadeKart.Stats
                    {
                        Steer = Banana.Values[0]
                    },
                    MaxTime = Banana.Duration
                });
                GameObject pfB = Instantiate(pfBoostUI, boostGrid);
                pfB.GetComponent<BoostUI>().Initialize(Banana.Duration, Color.yellow, "B");
                break;
        }
    }

    void Update()
    {
        for (int i = 0; i < currentID; i++)
        {
            float speedMod = 1.0f;

            ListOfCarStats[i].CurrentGas -= (Gas.ConsumeRate / 100.0f) * Time.deltaTime * ListOfCar[i].GetComponent<Rigidbody>().velocity.sqrMagnitude;
            if (ListOfCarStats[i].CurrentGas < Gas.MaxAmount * SlowThreshold)
                speedMod *= SlowRatio;

            ListOfCarStats[i].CurrentWheel -= (Wheel.ConsumeRate / 100.0f) * Time.deltaTime * ListOfCar[i].GetComponent<Rigidbody>().velocity.sqrMagnitude;
            if (ListOfCarStats[i].CurrentWheel < Wheel.MaxAmount * SlowThreshold)
                speedMod *= SlowRatio;

            ListOfCar[i].GetComponent<KartGame.KartSystems.ArcadeKart>().speedModifier = speedMod;
        }
        UpdateUI();

        flowManager.Undrivable = Undrivable();
    }

    private bool Undrivable()
    {
        return ListOfCarStats[PlayerID].CurrentGas <= 0.0f || ListOfCarStats[PlayerID].CurrentWheel <= 0.0f;
    }

    private void UpdateUI()
    {
        wheelBar.fillAmount = ListOfCarStats[0].CurrentWheel / Wheel.MaxAmount;
        gasBar.fillAmount = ListOfCarStats[0].CurrentGas / Gas.MaxAmount;
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

[System.Serializable]
public class RefillStats
{
    [Tooltip("Maxium Amount (Default: 50.0)")]
    [Range(10, 100)] public float MaxAmount;
    [Tooltip("The amount each Pick Up gives (Default: 25.0)")]
    [Range(5, 50)] public float PickUpAmount;
    [Tooltip("The rate at which it degrades (Default: 0.75)")]
    [Range(0.5f, 2.5f)] public float ConsumeRate;
}

[System.Serializable]
public class ConsumableStats
{
    [Tooltip("The amount of value change")]
    public float[] Values;
    [Tooltip("The Duration of the Effect in seconds")]
    public float Duration;
}