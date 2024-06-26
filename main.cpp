#include <iostream>
import AntohiRobert_counter2;
import AntohiRobert_counter;
import AntohiRobert_binpow;
int main (void)
{
  AntohiRobert_counter2::counter();
  AntohiRobert_counter::counter();
  int ans = AntohiRobert_binpow::binpow(2,5,79);
  std::cout<<ans<<std::endl;
  return 0;
}