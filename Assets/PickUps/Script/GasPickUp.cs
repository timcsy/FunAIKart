public class GasPickUp : PickUpClass
{
    public override void PickUpEffect(int CarID)
    {
        PickUpManager.instance.PickUp(PickUpManager.PickUpType.Gas, CarID);
    }
}