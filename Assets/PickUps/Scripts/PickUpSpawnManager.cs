using System.IO;
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
        // Using ramdom seed or not
        string config_file = Application.persistentDataPath + "/kart/PickUps.config";
        if (File.Exists(config_file))
        {
            string seed = File.ReadAllText(config_file).Trim();
            if (seed != "")
            {
                // Use random seed if the config file is not empty
                Random.InitState(int.Parse(seed));
            }
        }
        else
        {
            // Disable PickUps if the config file doesn't exist
            var PickUpLocations = GameObject.FindGameObjectsWithTag("PickUps");
            foreach (GameObject p in PickUpLocations)
            {
                p.SetActive(false);
            }
        }

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
            int childCount = t.childCount;
            for (int x = 0; x < childCount; x++)
            {
                if (t.GetChild(x).childCount > 0)
                    Destroy(t.GetChild(x).GetChild(0).gameObject);
                int i = Random.Range(0, Refill.ItemCount);
                Instantiate(Refill.ListOfItemsToSpawn[i], t.GetChild(x).position, Quaternion.identity, t.GetChild(x));
            }
        }
    }

    private void SpawnConsuamble()
    {
        foreach (Transform t in Consuamble.ListOfLocations)
        {
            int childCount = t.childCount;
            for (int x = 0; x < childCount; x++)
            {
                if (t.GetChild(x).childCount > 0)
                    Destroy(t.GetChild(x).GetChild(0).gameObject);
                int i = Random.Range(0, Consuamble.ItemCount);
                Instantiate(Consuamble.ListOfItemsToSpawn[i], t.GetChild(x).position, Quaternion.identity, t.GetChild(x));
            }
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