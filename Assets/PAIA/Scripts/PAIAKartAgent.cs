using System.Collections.Generic;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;
using UnityEngine;
using KartGame.KartSystems;
using Unity.MLAgents.Sensors.Reflection;

public class PAIAKartAgent : Agent, IInput
{
    [SerializeField]
    private GameObject TrainingInstance;
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
    private float angle;

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
            AddReward(10.0f);
        else
            AddReward(-10.0f);

        EndEpisode();
    }

    private void CorrectCheckPoint()
    {
        AddReward(10.0f);
    }

    private void WrongCheckPoint()
    {
        AddReward(-10.0f);
    }

    public void OutOfBound()
    {
        AddReward(-1000.0f);
    }

    public void Crash()
    {
        AddReward(-10.0f);
    }

    public void Grinding()
    {
        AddReward(-1.0f);
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
        transform.position = new Vector3(32.0f + Random.Range(-2.5f, 2.5f), 0.25f, 5.0f);
        transform.rotation = Quaternion.identity;

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

        SetReward(15.0f);   // Count Down Compensation
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        sensor.AddObservation(v);
        sensor.AddObservation(angle);
        sensor.AddObservation(progress);
        sensor.AddObservation(wheel);
        sensor.AddObservation(gas);
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        InterpretDiscreteActions(actionBuffers);
        //AddReward(-0.1f);
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        var discreteActionsOut = actionsOut.DiscreteActions;
        var continuousActionsOut = actionsOut.ContinuousActions;
        discreteActionsOut[0] = Input.GetButton(AccelerateButtonName) ? 1 : 0;
        discreteActionsOut[1] = Input.GetButton(BrakeButtonName) ? 1 : 0;
        continuousActionsOut[0] = Input.GetAxis(TurnInputName);
    }

    void InterpretDiscreteActions(ActionBuffers actionBuffers)
    {
        m_Acceleration = actionBuffers.DiscreteActions[0] > 0.5f;     // { 0, 1 }
        m_Brake = actionBuffers.DiscreteActions[1] > 0.5f;            // { 0, 1 }
        m_Steering = actionBuffers.ContinuousActions[0];              // [-1, 1 ]
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
        // Debug.Log(GetCumulativeReward());
        // Debug.Log("P: " + progress + ", A: " + angle + ",\nV: " + v + ", G: " + gas + ", W: " + wheel);
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