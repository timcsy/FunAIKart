using UnityEngine;

public class TrainingCheckPoints : MonoBehaviour
{
    private int cpCount;
    private int currentIndex;

    public static TrainingCheckPoints instance;

    public delegate void CP();
    public CP OnCorrectCheckPoint;
    public CP OnWrongCheckPoint;

    private PAIAKartAgent m_PAIAKart;
    private Transform PlayerCar;
    private float totalDistance;
    private float currentDistance;

    void Awake()
    {
        instance = this;
    }

    void Start()
    {
        cpCount = transform.childCount;
        ResetEp();

        for (int i = 0; i < cpCount; i++)
            transform.GetChild(i).GetComponent<SingleCheckPoint>().SetID(i);

        PAIAKartAgent[] karts = FindObjectsOfType<PAIAKartAgent>();
        if (karts.Length > 0 && !m_PAIAKart)
            m_PAIAKart = karts[0];

        PlayerCar = m_PAIAKart.transform;
        CalculateTotal();
    }

    private void CalculateTotal()
    {
        totalDistance = 0;

        // Distance between each Checkpoint
        for (int i = 0; i < cpCount - 1; i++)
            totalDistance += FastDistance2D(transform.GetChild(i).position, transform.GetChild(i + 1).position);

        // From First Checkpoint to Spawn
        totalDistance += FastDistance2D(transform.GetChild(0).position, PlayerCar.position);
    }

    void LateUpdate()
    {
        CalculateProgress();
    }

    private void CalculateProgress()
    {
        int count = cpCount - currentIndex;
        currentDistance = 0;

        for (int i = currentIndex; i < cpCount - 1; i++)
            currentDistance += FastDistance2D(transform.GetChild(i).position, transform.GetChild(i + 1).position);

        currentDistance += FastDistance2D(transform.GetChild(currentIndex).position, PlayerCar.position);

        float p = 1 - (currentDistance / totalDistance);
        m_PAIAKart.progress = Mathf.Round(p * 10000) / 10000.0f;
    }

    public void ResetEp()
    {
        currentIndex = 0;
    }

    public void CheckPoint(int id)
    {
        if (id == currentIndex)
        {
            currentIndex = (currentIndex + 1) % cpCount;
            OnCorrectCheckPoint?.Invoke();
        }
        else
            OnWrongCheckPoint?.Invoke();
    }

    public Vector3 GetNextDirection()
    {
        return transform.GetChild(currentIndex).forward;
    }

    private float FastDistance2D(Vector3 a, Vector3 b)
    {
        return Mathf.Pow(a.x - b.x, 2) + Mathf.Pow(a.z - b.z, 2);
    }
}