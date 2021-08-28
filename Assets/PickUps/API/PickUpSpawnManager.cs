using UnityEngine;

public class PickUpSpawnManager : MonoBehaviour
{
    public SpawnType Refill;
    public SpawnType Consuamble;

    [SerializeField]
    [Tooltip("The Time it takes to spawn a new set of PickUps (Default: 10.0)")]
    private float SpawnTimeGap;
    private float SpawnTimer;

    void Start()
    {
        Refill.ListOfLocations = new Transform[Refill.SpawnPointCount];
        Consuamble.ListOfLocations = new Transform[Consuamble.SpawnPointCount];

        for (int i = 0; i < Refill.SpawnPointCount; i++)
            Refill.ListOfLocations[i] = Refill.ParentTransform.GetChild(i);

        for (int i = 0; i < Consuamble.SpawnPointCount; i++)
            Consuamble.ListOfLocations[i] = Consuamble.ParentTransform.GetChild(i);

        SpawnTimer = -1;
    }

    void Update()
    {
        if (Time.time > SpawnTimer)
        {
            SpawnRefill();
            SpawnConsuamble();
            SpawnTimer = Time.time + SpawnTimeGap;
        }
    }

    private void SpawnRefill()
    {
        foreach (Transform t in Refill.ListOfLocations)
        {
            int i;
            if (t.GetChild(0).childCount > 0)
                Destroy(t.GetChild(0).GetChild(0).gameObject);
            i = Random.Range(0, Refill.ItemCount);
            Instantiate(Refill.ListOfItemsToSpawn[i], t.GetChild(0).position, Quaternion.identity, t.GetChild(0));

            if (t.GetChild(1).childCount > 0)
                Destroy(t.GetChild(1).GetChild(0).gameObject);
            i = Random.Range(0, Refill.ItemCount);
            Instantiate(Refill.ListOfItemsToSpawn[i], t.GetChild(1).position, Quaternion.identity, t.GetChild(1));

            if (t.GetChild(2).childCount > 0)
                Destroy(t.GetChild(2).GetChild(0).gameObject);
            i = Random.Range(0, Refill.ItemCount);
            Instantiate(Refill.ListOfItemsToSpawn[i], t.GetChild(2).position, Quaternion.identity, t.GetChild(2));
        }
    }

    private void SpawnConsuamble()
    {
        foreach (Transform t in Consuamble.ListOfLocations)
        {
            int i;
            if (t.GetChild(0).childCount > 0)
                Destroy(t.GetChild(0).GetChild(0).gameObject);
            i = Random.Range(0, Consuamble.ItemCount);
            Instantiate(Consuamble.ListOfItemsToSpawn[i], t.GetChild(0).position, Quaternion.identity, t.GetChild(0));

            if (t.GetChild(1).childCount > 0)
                Destroy(t.GetChild(1).GetChild(0).gameObject);
            i = Random.Range(0, Consuamble.ItemCount);
            Instantiate(Consuamble.ListOfItemsToSpawn[i], t.GetChild(1).position, Quaternion.identity, t.GetChild(1));

            if (t.GetChild(2).childCount > 0)
                Destroy(t.GetChild(2).GetChild(0).gameObject);
            i = Random.Range(0, Consuamble.ItemCount);
            Instantiate(Consuamble.ListOfItemsToSpawn[i], t.GetChild(2).position, Quaternion.identity, t.GetChild(2));
        }
    }
}

[System.Serializable]
public class SpawnType
{
    [Header("Prefabs")]
    [Tooltip("Prefabs in Assets/PickUps/Prefabs")]
    public GameObject[] ListOfItemsToSpawn;

    [Header("Object in Scene")]
    [Tooltip("The ===== *** POINTS ===== GameObject")]
    public Transform ParentTransform;

    [HideInInspector]
    public Transform[] ListOfLocations;

    public int ItemCount
    {
        get
        {
            return ListOfItemsToSpawn.Length;
        }
    }
    public int SpawnPointCount
    {
        get
        {
            return ParentTransform.childCount;
        }
    }
}