using UnityEngine;

public class TrainingCheckPoints : MonoBehaviour
{
    private int cpCount;
    private int currentIndex;

    public delegate void CP();
    public static CP OnCorrectCheckPoint;
    public static CP OnWrongCheckPoint;

    void Start()
    {
        cpCount = transform.childCount;
        currentIndex = 0;

        for (int i = 0; i < cpCount; i++)
            transform.GetChild(i).GetComponent<SingleCheckPoint>().SetID(i);
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
}