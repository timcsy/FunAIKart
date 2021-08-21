using UnityEngine;

public class PickUpSpawnManager : MonoBehaviour
{
    [SerializeField]
    [Tooltip("PickUp Prefabs in Assets/PickUps/Prefabs")]
    private GameObject[] ListOfItemsToSpawn;

    [SerializeField]
    [Tooltip("The ===== SPAWN POINTS ===== GameObject")]
    private Transform SpawnPointParent;
    private Transform[] ListOfSpawnLocations;

    private int ItemCount;

    [SerializeField]
    [Tooltip("The Time it takes to spawn a new set of PickUps (Default: 10.0)")]
    private float SpawnTimeGap;
    private float SpawnTimer;

    void Start()
    {
        ItemCount = SpawnPointParent.childCount;
        ListOfSpawnLocations = new Transform[ItemCount];
        for (int i = 0; i < ItemCount; i++)
            ListOfSpawnLocations[i] = SpawnPointParent.GetChild(i);
        SpawnTimer = -1;
    }

    void Update()
    {
        if (Time.time > SpawnTimer)
        {
            foreach (Transform t in ListOfSpawnLocations)
            {
                int i;
                if (t.GetChild(0).childCount > 0)
                    Destroy(t.GetChild(0).GetChild(0).gameObject);
                i = Random.Range(0, ItemCount);
                Instantiate(ListOfItemsToSpawn[i], t.GetChild(0).position, Quaternion.identity, t.GetChild(0));

                if (t.GetChild(1).childCount > 0)
                    Destroy(t.GetChild(1).GetChild(0).gameObject);
                i = Random.Range(0, ItemCount);
                Instantiate(ListOfItemsToSpawn[i], t.GetChild(1).position, Quaternion.identity, t.GetChild(1));

                if (t.GetChild(2).childCount > 0)
                    Destroy(t.GetChild(2).GetChild(0).gameObject);
                i = Random.Range(0, ItemCount);
                Instantiate(ListOfItemsToSpawn[i], t.GetChild(2).position, Quaternion.identity, t.GetChild(2));
            }
            SpawnTimer = Time.time + SpawnTimeGap;
        }
    }
}