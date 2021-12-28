using UnityEngine;

[RequireComponent(typeof(BoxCollider))]
public class SingleCheckPoint : MonoBehaviour
{
    private int myID;

    public void SetID(int id)
    {
        myID = id;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.transform.parent.CompareTag("Player"))
            transform.parent.GetComponent<TrainingCheckPoints>().CheckPoint(myID);
    }
}