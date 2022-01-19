using System.Collections;
using System.Collections.Generic;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using UnityEngine;
using KartGame.KartSystems;
using Unity.MLAgents.Sensors.Reflection;
using UnityEngine.SceneManagement;
using Unity.MLAgents.Demonstrations;

public class PAIAKartAgent : Agent, IInput
{
    [Header("Input Settings")]
    public string TurnInputName = "Horizontal";
    public string AccelerateButtonName = "Accelerate";
    public string BrakeButtonName = "Brake";

    // Observations
    [Observable(name: "progress"), HideInInspector]
    public float progress; // [0, 1]
    [Observable(name: "usedtime"), HideInInspector]
    public float usedtime; // [0, 60]
    [Observable(name: "velocity"), HideInInspector]
    public float velocity
    {   // [0, oo)
        get
        {
            return GetComponent<Rigidbody>().velocity.magnitude * 5.0f;
        }
    }
    [Observable(name: "wheel"), HideInInspector]
    public float wheel; // [0, 1]
    [Observable(name: "gas"), HideInInspector]
    public float gas; // [0, 1]
    [Observable(name: "nitro"), HideInInspector]
    public int nitro; // number of nitros
    [Observable(name: "turtle"), HideInInspector]
    public int turtle; // number of turtles
    [Observable(name: "banana"), HideInInspector]
    public int banana; // number of bananas
    // events
    [Observable(name: "win"), HideInInspector]
    public bool win;
    [Observable(name: "timeout"), HideInInspector]
    public bool timeout;
    [Observable(name: "undrivable"), HideInInspector]
    public bool undrivable;

    // Actions
    bool m_Acceleration; // { 0, 1 }
    bool m_Brake; // { 0, 1 }
    float m_Steering; // [-1, 1]

    // Other variables
    [HideInInspector]
    public ArcadeKart m_Kart;
    [HideInInspector]
    public Rigidbody m_Rigidbody;
    [HideInInspector]
    DemonstrationRecorder m_Demo;
    [HideInInspector]
    public SingleUI m_UI;
    [HideInInspector]
    public float CurrentWheel;
    [HideInInspector]
    public float CurrentGas;
    private List<KartEffect> effects;
    bool isReloading = false;
    
    void Start()
    {
        string name = GetComponent<BehaviorParameters>().BehaviorName + "?team=" + GetComponent<BehaviorParameters>().TeamId;
        Debug.Log(name);
        InitDemo(true, "PAIA/Demo", "kart", 10000);
        m_Kart = GetComponent<ArcadeKart>();
        m_Rigidbody = GetComponent<Rigidbody>();
        m_UI = GetComponent<SingleUI>();
    }

    void InitDemo(bool Record=true, string DemonstrationDirectory = "PAIA/Demo", string DemonstrationName="demo", int NumStepsToRecord=10000)
    {
        m_Demo = gameObject.AddComponent(typeof(DemonstrationRecorder)) as DemonstrationRecorder;
        m_Demo.NumStepsToRecord = NumStepsToRecord;
        m_Demo.DemonstrationName = DemonstrationName;
        m_Demo.DemonstrationDirectory = DemonstrationDirectory;
        m_Demo.Record = Record;
    }

    public override void OnEpisodeBegin()
    {
        if(!m_Kart) m_Kart = GetComponent<ArcadeKart>();
        // Consider making Awake public or exposing an Initialize method for it.
        m_Kart.SendMessage("Awake"); // For some reason "OnEpisodeBegin" gets called before m_Kart.Awake, so this is necessary
        progress = 0;
        m_Kart.Rigidbody.velocity = default;
        wheel = 1;
        gas = 1;
        nitro = 0;
        turtle = 0;
        banana = 0;
        win = false;
        timeout = false;
        undrivable = false;
        m_Acceleration = false;
        m_Brake = false;
        m_Steering = 0f;
        effects = new List<KartEffect>();
        PickUpManager.instance.RegisterKart(this);
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        // SetReward(0.1f);
        InterpretDiscreteActions(actionBuffers);
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        var discreteActionsOut = actionsOut.DiscreteActions;
        var continuousActionsOut = actionsOut.ContinuousActions;
        discreteActionsOut[0] = Input.GetButton(AccelerateButtonName)? 1: 0;
        discreteActionsOut[1] = Input.GetButton(BrakeButtonName)? 1: 0;
        continuousActionsOut[0] = Input.GetAxis(TurnInputName);
    }

    void InterpretDiscreteActions(ActionBuffers actionBuffers)
    {
        m_Acceleration = actionBuffers.DiscreteActions[0] > 0.5; // { 0, 1 }
        m_Brake = actionBuffers.DiscreteActions[1] > 0.5; // { 0, 1 }
        m_Steering = actionBuffers.ContinuousActions[0]; // [-1, 1]
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

    private void OnCollisionEnter(Collision collision) {
        if (!collision.gameObject.GetComponent<PickUpClass>())
        { 
            // EndGame();
        }
        if (collision.gameObject.tag == "Outside")
        {
            EndGame();
        }
    }

    public void UpdateRefill(float wheel, float gas)
    {
        this.wheel = wheel;
        this.gas = gas;
        if (m_UI) if (m_UI.enabled) m_UI.UpdateRefill(this.wheel, this.gas);
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
        if (m_UI) if (m_UI.enabled) m_UI.ApplyEffect(type, duration);
    }

    void Update()
    {
        // Debug.Log("Progress: " + progress + "%");
        effects.RemoveAll(EffectTimeout); // Remove by the condition
        // Debug.Log("Effects: " + effects.Count + ", Nitro:" + nitro + ", Turtle:" + turtle + ", Banana:" + banana);
        if (win || timeout || undrivable)
        {
            EndGame();
        }
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

    public void EndGame()
    {
        EndEpisode();
        if (GetComponent<BehaviorParameters>().IsInHeuristicMode())
        {
            #if UNITY_EDITOR
            // Application.Quit() does not work in the editor so
            // UnityEditor.EditorApplication.isPlaying need to be set to false to end the game
            UnityEditor.EditorApplication.isPlaying = false;
            #else
            Application.Quit();
            #endif
        }
    }

    public void Reload()
    {
        // Deprecated
        if(!isReloading)
        {
            // Ensure that the scene does not get loaded multiple times in the same frame.
            isReloading = true;
            // Academy.Instance.Dispose();
            SceneManager.LoadScene(SceneManager.GetActiveScene().name, LoadSceneMode.Single);
        }
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