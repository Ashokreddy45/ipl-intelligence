# Feature scope and data limitations

## Supported by the current source
- Delivery-level batter, non-striker and bowler names
- Runs off bat, extras and listed extras types
- Wicket type, dismissed player and listed fielders
- Match ID, season, date, venue, innings and over/delivery sequence
- Match metadata from the paired information files, including teams and available outcomes

## Not directly supported
- Shot name (pull, cut, sweep, drive)
- Ball pitch coordinates, line, length, speed, swing or seam movement
- Wagon-wheel coordinates and exact shot direction
- Field placement or complete ball-tracking data

## Safe analysis language
Use “runs and dismissals against bowler X” rather than claiming a batter is weak to a delivery type that is not recorded. A high head-to-head dismissal count alone does not prove a tactical weakness; account for balls faced, innings context, season, and sample size.
