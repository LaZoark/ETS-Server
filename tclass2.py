from tclass import AA


vv = AA()
vv.val

class BB:
  def __init__(self) -> None:
    val_2: int = 4
    print(f'Original {vv.val=}')
    vv.val += val_2
    print(f'[BB] adding {val_2} to {vv.val=}')
    
    vv.later_call()

vv.val=4    
BB()
