
class AA:
  val: int = 0
  def __init__(self) -> None:
    pass
    
    
  def later_call(self):
    print(f'adding 1 to {self.val=} ', end='')
    self.val += 1
    print(f', becaming {self.val=}')