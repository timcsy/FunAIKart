using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

public enum PickUpType { Wheel, Gas, Nitro, Turtle, Banana }

/// <summary>
/// The class that communicates between Item and Car group
/// </summary>
public class PickUpManager : MonoBehaviour
{
    // Singleton
    public static PickUpManager instance;

    [SerializeField]
    private GameFlowManager flowManager;

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

    private List<PAIAKartAgent> karts;

    void Awake()
    {
        instance = this;
        karts = new List<PAIAKartAgent>();
    }

    void Start()
    {
        List<GameObject> ListOfCar = new List<GameObject>(GameObject.FindGameObjectsWithTag("Player"));
        foreach (GameObject c in ListOfCar)
            RegisterKart(c.GetComponent<PAIAKartAgent>());
    }

    public void RegisterKart(PAIAKartAgent kart)
    {
        kart.CurrentWheel = Wheel.MaxAmount;
        kart.CurrentGas = Gas.MaxAmount;
        if (!karts.Contains(kart)) karts.Add(kart);
    }

    public void PickUp(PickUpType pickUpType, PAIAKartAgent kart)
    {
        switch (pickUpType)
        {
            case PickUpType.Wheel:
                kart.CurrentWheel += Wheel.PickUpAmount;
                if (kart.CurrentWheel > Wheel.MaxAmount)
                    kart.CurrentWheel = Wheel.MaxAmount;
                break;
            case PickUpType.Gas:
                kart.CurrentGas += Gas.PickUpAmount;
                if (kart.CurrentGas > Gas.MaxAmount)
                    kart.CurrentGas = Gas.MaxAmount;
                break;
            case PickUpType.Nitro:
                kart.m_Kart.AddPowerup(new KartGame.KartSystems.ArcadeKart.StatPowerup
                {
                    modifiers = new KartGame.KartSystems.ArcadeKart.Stats
                    {
                        Acceleration = Nitro.Values[0],
                        TopSpeed = Nitro.Values[1]
                    },
                    MaxTime = Nitro.Duration
                });
                kart.ApplyEffect(PickUpType.Nitro, Nitro.Duration);
                break;
            case PickUpType.Turtle:
                kart.m_Kart.AddPowerup(new KartGame.KartSystems.ArcadeKart.StatPowerup
                {
                    modifiers = new KartGame.KartSystems.ArcadeKart.Stats
                    {
                        Acceleration = Turtle.Values[0],
                        TopSpeed = Turtle.Values[1]
                    },
                    MaxTime = Turtle.Duration
                });
                kart.ApplyEffect(PickUpType.Turtle, Turtle.Duration);
                break;
            case PickUpType.Banana:
                kart.m_Kart.AddPowerup(new KartGame.KartSystems.ArcadeKart.StatPowerup
                {
                    modifiers = new KartGame.KartSystems.ArcadeKart.Stats
                    {
                        Steer = Banana.Values[0]
                    },
                    MaxTime = Banana.Duration
                });
                kart.ApplyEffect(PickUpType.Banana, Banana.Duration);
                break;
        }
    }

    void Update()
    {
        int numKarts = karts.Count;
        for (int i = 0; i < numKarts; i++)
        {
            float speedMod = 1.0f;

            karts[i].CurrentWheel -= (Wheel.ConsumeRate / 100.0f) * Time.deltaTime * karts[i].m_Rigidbody.velocity.sqrMagnitude;
            if (karts[i].CurrentWheel < Wheel.MaxAmount * SlowThreshold)
                speedMod *= SlowRatio;

            karts[i].CurrentGas -= (Gas.ConsumeRate / 100.0f) * Time.deltaTime * karts[i].m_Rigidbody.velocity.sqrMagnitude;
            if (karts[i].CurrentGas < Gas.MaxAmount * SlowThreshold)
                speedMod *= SlowRatio;

            karts[i].m_Kart.speedModifier = speedMod;
            var wheel = karts[i].CurrentWheel / Wheel.MaxAmount;
            var gas = karts[i].CurrentGas / Gas.MaxAmount;
            karts[i].UpdateRefill(wheel, gas);
            if (karts[i].CurrentGas <= 0.0f || karts[i].CurrentWheel <= 0.0f)
            {
                karts[i].undrivable = true;
                karts[i].m_Kart.enabled = false;
            }
        }

        flowManager.Undrivable = Undrivable();
        UpdateEvent();
    }

    private bool Undrivable()
    {
        bool undrivable = true;
        int numKarts = karts.Count;
        for (int i = 0; i < numKarts; i++)
        {
            if (!karts[i].undrivable)
            {
                undrivable = false;
                break;
            }
        }
        return undrivable;
    }

    private void UpdateEvent()
    {
        GameFlowManager.EndGameReason Event = flowManager.Event;
        for (int i = 0; i < karts.Count; i++)
        {
            switch (Event)
            {
                case GameFlowManager.EndGameReason.Win:
                    karts[i].win = true;
                    break;
                case GameFlowManager.EndGameReason.TimeOut:
                    karts[i].timeout = true;
                    break;
            }
            
            karts[i].usedtime = flowManager.UsedTime;
        }
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