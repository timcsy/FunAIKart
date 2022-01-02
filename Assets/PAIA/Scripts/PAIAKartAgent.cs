using System.Collections.Generic;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;
using UnityEngine;
using KartGame.KartSystems;
using Unity.MLAgents.Sensors.Reflection;

public class PAIAKartAgent : Agent, IInput
{
    [Header("Debug")]
    [SerializeField]
    private bool ShowReward;
    [SerializeField]
    private bool ShowObservation;

    [Header("Training Settings")]
    [SerializeField] [Tooltip("New Version?")]
    private bool UseDiscrete;

    [SerializeField]
    private GameObject TrainingInstance;

    [SerializeField]
    private Transform SpawnPoint;

    private GameObject instance;

    [Header("Input Settings")]
    public string TurnInputName = "Horizontal";
    public string AccelerateButtonName = "Accelerate";
    public string BrakeButtonName = "Brake";

    [Observable(name: "velocity"), HideInInspector]
    public float velocity   // [0, oo)
    {
        get
        {
            return GetComponent<Rigidbody>().velocity.magnitude * 5.0f;
        }
    }

    // Observations
    [Observable(name: "progress"), HideInInspector]
    public float progress;  // (-oo, 1]
    [Observable(name: "angle"), HideInInspector]
    public float angle;     // [-1, 1]

    [Observable(name: "wheel"), HideInInspector]
    public float wheel;     // [0, 1]
    [Observable(name: "gas"), HideInInspector]
    public float gas;       // [0, 1]

    [Observable(name: "nitro"), HideInInspector]
    public int nitro;   // number of nitros effect
    [Observable(name: "turtle"), HideInInspector]
    public int turtle;  // number of turtles effect
    [Observable(name: "banana"), HideInInspector]
    public int banana;  // number of bananas effect

    [Observable(name: "undrivable"), HideInInspector]
    public bool undrivable;

    // Actions
    bool m_Acceleration;    // { 0, 1 }
    bool m_Brake;           // { 0, 1 }
    float m_Steering;       // [-1, 1 ]

    // misc.
    [HideInInspector]
    public ArcadeKart m_Kart;
    [HideInInspector]
    public Rigidbody m_Rigidbody;
    [HideInInspector]
    public SingleUI m_UI;
    [HideInInspector]
    public float CurrentWheel;
    [HideInInspector]
    public float CurrentGas;

    private List<KartEffect> effects;
    private float v;

    public override void CollectObservations(VectorSensor sensor)
    {
        sensor.AddObservation(v);
        sensor.AddObservation(progress);
        sensor.AddObservation(angle);

        sensor.AddObservation(wheel);
        sensor.AddObservation(gas);
    }

    void Start()
    {
        m_Kart = GetComponent<ArcadeKart>();
        m_Rigidbody = GetComponent<Rigidbody>();
        m_UI = GetComponent<SingleUI>();

        TrainingCheckPoints.instance.OnCorrectCheckPoint += CorrectCheckPoint;
        TrainingCheckPoints.instance.OnWrongCheckPoint += WrongCheckPoint;
    }

    private void GameEnded(bool win)
    {
        if (win)
            AddReward(5.0f);
        else
            AddReward(-2.5f);

        EndEpisode();
    }

    private void CorrectCheckPoint()
    {
        AddReward(1.0f);
    }

    private void WrongCheckPoint()
    {
        AddReward(-1.0f);
    }

    public void OutOfBound()
    {
        SetReward(-10.0f);
        EndEpisode();
    }

    public void Crash()
    {
        AddReward(-2.0f);
    }

    public void Grinding()
    {
        AddReward(-0.1f);
    }

    public override void OnEpisodeBegin()
    {
        if(instance != null)
        {
            GameFlowManager.OnGameEnd -= GameEnded;
            Destroy(instance);
        }

        instance = Instantiate(TrainingInstance, Vector3.zero, Quaternion.identity);
        GameFlowManager.OnGameEnd += GameEnded;
        TrainingCheckPoints.instance.ResetEp();

        m_Kart.Rigidbody.velocity = Vector3.zero;
        m_Kart.Rigidbody.angularVelocity = Vector3.zero;
        transform.position = SpawnPoint.position + new Vector3(Random.Range(-2.5f, 2.5f), 0.0f, 0.0f);
        transform.rotation = SpawnPoint.rotation;

        effects = new List<KartEffect>();
        nitro = 0;
        turtle = 0;
        banana = 0;

        wheel = 1.0f;
        gas = 1.0f;

        undrivable = false;

        PickUpManager.instance.RegisterKart(this);

        m_Acceleration = false;
        m_Brake = false;
        m_Steering = 0f;
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        InterpretDiscreteActions(actionBuffers);
    }

    private void InterpretDiscreteActions(ActionBuffers actionBuffers)
    {
        if (!UseDiscrete)
        {
            m_Acceleration = actionBuffers.DiscreteActions[0] > 0.5f;     // { 0, 1 }
            m_Brake = actionBuffers.DiscreteActions[1] > 0.5f;            // { 0, 1 }
            m_Steering = actionBuffers.ContinuousActions[0];              // [-1, 1 ]
        }
        else
        {
            m_Acceleration = actionBuffers.DiscreteActions[0] == 2;     // { 0, 1 }
            m_Brake = actionBuffers.DiscreteActions[0] == 0;            // { 0, 1 }
            switch (actionBuffers.DiscreteActions[1])                   // [-1, 1 ]
            {
                case 0:
                    m_Steering = -0.5f;
                    break;
                case 1:
                    m_Steering = 0.0f;
                    break;
                case 2:
                    m_Steering = 0.5f;
                    break;
            }
        }
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        if (!UseDiscrete)
        {
            var discreteActionsOut = actionsOut.DiscreteActions;
            var continuousActionsOut = actionsOut.ContinuousActions;
            discreteActionsOut[0] = Input.GetButton(AccelerateButtonName) ? 1 : 0;
            discreteActionsOut[1] = Input.GetButton(BrakeButtonName) ? 1 : 0;
            continuousActionsOut[0] = Input.GetAxisRaw(TurnInputName);
        }
        else
        {
            var discreteActionsOut = actionsOut.DiscreteActions;
            if (Input.GetButton(AccelerateButtonName))
                discreteActionsOut[0] = 2;
            else if (Input.GetButton(BrakeButtonName))
                discreteActionsOut[0] = 0;
            else
                discreteActionsOut[0] = 1;

            if (Input.GetAxis(TurnInputName) < 0)
                discreteActionsOut[1] = 0;
            else if (Input.GetAxis(TurnInputName) > 0)
                discreteActionsOut[1] = 2;
            else
                discreteActionsOut[1] = 1;
        }
    }

    public InputData GenerateInput()
    {
        return new InputData
        {
            Accelerate = m_Acceleration,
            Brake = m_Brake,
            TurnInput = m_Steering
        };
    }

    public void UpdateRefill(float wheel, float gas)
    {
        this.wheel = wheel;
        this.gas = gas;
        if (m_UI != null && m_UI.enabled)
            m_UI.UpdateRefill(this.wheel, this.gas);
    }

    public void ApplyEffect(PickUpType type, float duration)
    {
        KartEffect effect = new KartEffect(type, duration, Time.time);
        switch (type)
        {
            case PickUpType.Nitro: nitro++; break;
            case PickUpType.Turtle: turtle++; break;
            case PickUpType.Banana: banana++; break;
        }
        effects.Add(effect);
        if (m_UI != null && m_UI.enabled)
            m_UI.ApplyEffect(type, duration);
    }

    void Update()
    {
        v = velocity / 180.0f;
        angle = Vector3.Dot(transform.forward, TrainingCheckPoints.instance.GetNextDirection());

        effects.RemoveAll(EffectTimeout);
        if (ShowReward) Debug.Log(GetCumulativeReward());
        if (ShowObservation) Debug.Log("V: " + v + ", A: " + angle + "\nP: " + progress + ", W: " + wheel + ", G: " + gas);
        // Debug.Log("Effects: " + effects.Count + ", Nitro:" + nitro + ", Turtle:" + turtle + ", Banana:" + banana);
    }

    private bool EffectTimeout(KartEffect effect)
    {
        bool timeout = Time.time - effect.startTime >= effect.duration;
        if (timeout)
        {
            switch (effect.type)
            {
                case PickUpType.Nitro: nitro--; break;
                case PickUpType.Turtle: turtle--; break;
                case PickUpType.Banana: banana--; break;
            }
        }
        return timeout;
    }
}

public struct KartEffect
{
    public PickUpType type;
    public float duration;
    public float startTime;
    public KartEffect(PickUpType type, float duration, float startTime)
    {
        this.type = type;
        this.duration = duration;
        this.startTime = startTime;
    }
}