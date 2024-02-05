# M-League

 Database project of analyzing M-League data

## Introduction

The M-League in Japan is a professional mahjong league organized by the Japan Mahjong Association. The general format is:

1. **Participating Teams:** The M-League typically consists of multiple teams representing different cities or regions. These teams are composed of well-known professional mahjong players, representing their respective areas in the competition.

2. **Competition Period:** The M-League generally includes regular-season and playoff phases. The regular season usually starts at the beginning of the season and involves matches between all participating teams.

3. **Match Formats:** The competition in M-League includes both team matches and individual matches. In team matches, multiple players from a team collaborate to compete against other teams, while individual matches involve each player competing independently.

4. **Scoring System:** During the regular season, winning teams or players earn **scores**, and the rankings are determined based on these **scores** to decide qualification for the playoffs.

5. **Playoffs:** After the regular season concludes, the top-ranked teams advance to the playoffs. The playoffs typically follow an elimination format until the annual champion is determined.


To simplify, this project only considers team matches during regular season.

## Competition Rules

1. Typically, there are two matches on each competition day. In each match, one player from each of the four pre-arranged teams participates.
2. The mahjong competition involves **point** calculation rather than **score** calculation. After the end of each round, points are converted into scores using the following rules:
   - Each player starts with 25,000 points. Throughout the match, each player gains or loses points, but the total sum of points for all four players remains constant at 100,000. The smallest unit for point calculation is 100.
   - After a match concludes, the basic score is calculated as follows: (total points at the end - 30,000) / 1000.
   - The basic score is then combined with ranking rewards to determine the total score. Ranking rewards are as follows: 1st place +50, 2nd place +10, 3rd place -10, 4th place -30. The smallest unit for score calculation is 0.1.
   - In case of a tie in the total points at the end, players with the same points share the ranking score equally.
3. The sum of individual scores for each team constitutes the team score.

Currently, details during the competition process are not considered.

## Database Design

E-R diagram: [E-R Diagram](./resource/E-R Diagram.drawio)

Database design: [https://dbdiagram.io/d/M-League-65a34568ac844320aedc7e2b](https://dbdiagram.io/d/M-League-65a34568ac844320aedc7e2b)

## Common Query Logic

- Calculate the team rankings within a given time period.
- Calculate the individual rankings within a given time period.
- Determine the highest-scoring 1st place player in a single match.
- Calculate the lowest-scoring 4th place players in a single match.
- Calculate the rates of achieving first, second, third, and fourth place for an individual.
- Calculate the average points for achieving first, second, third, and fourth place.

## References

- https://mleaguedata.fun/
- https://www.bilibili.com/read/cv18948527/
- Twitter @penropin