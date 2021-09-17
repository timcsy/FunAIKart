public class NitroPickUp : PickUpClass
{
    public override void PickUpEffect(int CarID)
    {
        PickUpManager.instance.PickUp(PickUpManager.PickUpType.Nitro, CarID);
    }
}