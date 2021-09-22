using System.Collections;
using System.Collections.Generic;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;
using UnityEngine;
using KartGame.KartSystems;

public class PAIAKartAgent : Agent, IInput
{
    public string TurnInputName = "Horizontal";
    public string AccelerateButtonName = "Accelerate";
    public string BrakeButtonName = "Brake";

    ArcadeKart m_Kart;
    bool m_Acceleration;
    bool m_Brake;
    float m_Steering;
    
    void Start()
    {
        m_Kart = GetComponent<ArcadeKart>();
    }

    public override void OnEpisodeBegin()
    {
        m_Kart.Rigidbody.velocity = default;
        m_Acceleration = false;
        m_Brake = false;
        m_Steering = 0f;
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        InterpretDiscreteActions(actionBuffers);
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        var discreteActionsOut = actionsOut.DiscreteActions;
        var continuousActionsOut = actionsOut.ContinuousActions;
        discreteActionsOut[0] = Input.GetButton(AccelerateButtonName)? 1: -1;
        discreteActionsOut[1] = Input.GetButton(BrakeButtonName)? 1: -1;
        continuousActionsOut[0] = Input.GetAxis(TurnInputName);
    }

    void InterpretDiscreteActions(ActionBuffers actionBuffers)
    {
        m_Acceleration = actionBuffers.DiscreteActions[0] > 0; // {..., -1, 0, 1, ...}
        m_Brake = actionBuffers.DiscreteActions[1] > 0; // {..., -1, 0, 1, ...}
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
}
