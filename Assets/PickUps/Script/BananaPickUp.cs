public class BananaPickUp : PickUpClass
{
    public override void PickUpEffect(int CarID)
    {
        PickUpManager.instance.PickUp(PickUpManager.PickUpType.Banana, CarID);
    }
}