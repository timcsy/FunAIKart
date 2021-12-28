using System.Collections.Generic;
using UnityEngine;

public class TrackProgress : MonoBehaviour
{
    [SerializeField] [Tooltip("Sort from FinishLine to First")]
    private List<Transform> CheckPoints;

    [SerializeField]
    private Objective objective;

    private PAIAKartAgent m_PAIAKart;
    private Transform PlayerCar;
    private float totalDistance;
    private float currentDistance;

    private int CheckPointCount;

    void Start()
    {
        PAIAKartAgent[] karts = FindObjectsOfType<PAIAKartAgent>();
        if (karts.Length > 0 && !m_PAIAKart)
            m_PAIAKart = karts[0];

        PlayerCar = m_PAIAKart.transform;
        CheckPointCount = CheckPoints.Count;
        CalculateTotal();
    }

    void LateUpdate()
    {
        CalculateProgress();
    }

    private void CalculateTotal()
    {
        totalDistance = 0;

        // Distance between each Checkpoint
        for (int i = 0; i < CheckPointCount - 1; i++)
            totalDistance += FastDistance2D(CheckPoints[i].position, CheckPoints[i + 1].position);

        // From First Checkpoint to Spawn
        totalDistance += FastDistance2D(CheckPoints[CheckPointCount - 1].position, PlayerCar.position);
    }

    private void CalculateProgress()
    {
        int count = objective.NumberOfPickupsRemaining;
        currentDistance = 0;

        //  Still Checkpoint Lasts
        if (count > 0)
        {
            for (int i = 0; i < count - 1; i++)
                currentDistance += FastDistance2D(CheckPoints[i].position, CheckPoints[i + 1].position);

            currentDistance += FastDistance2D(CheckPoints[count - 1].position, PlayerCar.position);
        }

        float p = 1 - (currentDistance / totalDistance);
        m_PAIAKart.progress = Mathf.Round(p * 10000) / 10000.0f;
    }

    private float FastDistance2D(Vector3 a, Vector3 b)
    {
        return Mathf.Pow(a.x - b.x, 2) + Mathf.Pow(a.z - b.z, 2);
    }
}