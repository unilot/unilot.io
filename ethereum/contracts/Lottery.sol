pragma solidity ^0.4.13;

contract Lottery {
    enum State {
        NEW,
        STARTED,
        ENDED,
        REVOKED
    }

    struct Player {
        uint time;
    }

    State private state;       //Game state
    uint private betAmount;    //Size of single bet
    uint private totalAmount;  //Total amount that winner should get if game has guaranteed prize

    mapping(address => Player) players;  //Map of players and time they've participated
    address [] playersList;              //List of players
    address administrator;               //Administrator of the game

    //This vars are set after winning
    address winner;   //Account that won the lottery
    uint winnerIndex; //Index in array of players
    uint prize;       //Prize that was delivered to winner account

    event GameStarted(uint betAmount, uint totalAmount);
    event NewPlayerAdded(address player);
    event GameFinished(address winner, uint amount);

    //Modifier that restricts access to function only by admin
    modifier administratorRestricted() {
        require(msg.sender == administrator);
        _;
    }

    function Lottery(uint gambleAmount, uint prizeAmount) {
        state = State.STARTED;
        betAmount = gambleAmount;
        totalAmount = prizeAmount;
        administrator = msg.sender;
    }

    function ()
    payable {
        require(msg.sender != administrator);
        require(state == State.STARTED);
        require(msg.value == betAmount);
        require(players[msg.sender].time == 0);

        players[msg.sender].time = now;
        playersList.push(msg.sender);

        NewPlayerAdded(msg.sender);
    }

    function rand(uint minNum, uint maxNum)
    private
    administratorRestricted
    returns (uint) {
        //Randomization magic
        return (uint(block.blockhash(block.number - 1)) + now) % (maxNum - minNum + 1) + minNum;
    }

    function finish()
    payable
    administratorRestricted {
        require(state == State.STARTED);
        require(playersList.length >= 4);
        require(totalAmount > 0 && (this.balance >= totalAmount || this.balance + msg.value == totalAmount) );

        state = State.ENDED;

        winner = playersList[rand(0, (playersList.length - 1))];
        prize = calculatePrizeFromBalance();
        uint charityPrize = this.balance - prize;

        GameFinished(winner, prize);

        winner.transfer(prize);
        administrator.transfer(charityPrize);
    }

    function calculatePrizeFromBalance()
    private
    returns(uint) {
        return this.balance/2;
    }
}
