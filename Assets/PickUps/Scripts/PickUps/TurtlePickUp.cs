public class TurtlePickUp : PickUpClass
{
    public override void PickUpEffect(PAIAKartAgent kart)
    {
        PickUpManager.instance.PickUp(PickUpType.Turtle, kart);
    }
}