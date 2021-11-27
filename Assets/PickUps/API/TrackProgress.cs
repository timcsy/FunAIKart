using System.Collections.Generic;
using UnityEngine;

public class TrackProgress : MonoBehaviour
{
    [SerializeField] [Tooltip("From Last to First")]
    private List<Transform> CheckPoints;
    [SerializeField]
    private Transform FinishLine;
    [SerializeField]
    private Transform PlayerCar;
    [SerializeField]
    private Objective objective;

    private float totalDistance;
    private float currentDistance;

    private float progress;

    private int CheckPointCount;

    void Start()
    {
        CheckPointCount = CheckPoints.Count;
        CalculateTotal();
    }

    void LateUpdate()
    {
        CalculateProgress();
    }

    private void CalculateTotal()
    {
        // From Finish to Last Checkpoint
        totalDistance = FastDistance2D(CheckPoints[0].position, FinishLine.position);

        // Distance between each Checkpoint
        for (int i = 1; i < CheckPointCount; i++)
        {
            totalDistance += FastDistance2D(CheckPoints[i - 1].position, CheckPoints[i].position);
        }

        // From First Checkpoint to Spawn
        totalDistance += FastDistance2D(CheckPoints[CheckPointCount - 1].position, PlayerCar.position);
    }

    private void CalculateProgress()
    {
        int count = objective.NumberOfPickupsRemaining;
        //  Still Checkpoint Lasts
        if (count > 0)
        {
            currentDistance = FastDistance2D(CheckPoints[0].position, FinishLine.position);

            for (int i = 1; i < count; i++)
                currentDistance += FastDistance2D(CheckPoints[i - 1].position, CheckPoints[i].position);

            currentDistance += FastDistance2D(CheckPoints[count - 1].position, PlayerCar.position);
        }
        else
        {
            // From Finish to Player
            currentDistance = FastDistance2D(PlayerCar.position, FinishLine.position);
        }

        progress = Mathf.Round((1 - (currentDistance / totalDistance)) * 10000.0f) / 100.0f;
        Debug.Log("Progress: " + progress + "%");
    }

    private float FastDistance2D(Vector3 a, Vector3 b)
    {
        return Mathf.Pow(a.x - b.x, 2) + Mathf.Pow(a.z - b.z, 2);
    }
}