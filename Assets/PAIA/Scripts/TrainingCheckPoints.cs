using UnityEngine;

public class TrainingCheckPoints : MonoBehaviour
{
    private int cpCount;
    private int currentIndex;

    public static TrainingCheckPoints instance;

    public delegate void CP();
    public CP OnCorrectCheckPoint;
    public CP OnWrongCheckPoint;

    void Start()
    {
        instance = this;

        cpCount = transform.childCount;
        ResetEp();

        for (int i = 0; i < cpCount; i++)
            transform.GetChild(i).GetComponent<SingleCheckPoint>().SetID(i);
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
}