# pointnemo
Given a csv with lat lon points, find the point on earth that is furthest from any of those points. 

I used this to compute "Point Jose Nemo" based on the location sleuthing videos by Jose Monkey [https://www.tiktok.com/@the_josemonkey]. In each video, he tells us how far the nearest point he previously found is from the new point. This answers the question: "How big could that distance be?"

Said differently what point on earth is the furthest you could possibly be from a point that Jose Monkey has found? As of Nov 10 2024 that point is at (-23.148485293394128, -128.65007742588224) that is 5703.203320603806 kilometers away. That is pretty close to the Pitcairn IslandsE.

## Example Usage:

```
python3 pointNemo.py JoseMonkeys_Found_Locations_Nov10/Season_1.csv JoseMonkeys_Found_Locations_Nov10/Season_2.csv JoseMonkeys_Found_Locations_Nov10/Season_3.csv JoseMonkeys_Found_Locations_Nov10/Special_Episodes.csv
```
