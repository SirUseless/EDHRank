var drake = dragula([document.getElementById('left'), document.getElementById('right')], {
    accepts: function (el, target) {
        return !el.classList.contains('no-dnd')
    },
    moves: function (el, container, handle) {
        return !el.classList.contains('no-dnd')
    }
});

var crown = '<div id="crown" class=" card-content drag-elem center tooltipped" data-position="left" data-tooltip="Gañador da partida"><img src="../../static/crown.png" alt="" style="height: 30px; width: 35px"></div>';
var elCrown = document.createElement('div');
elCrown.innerHTML = crown;
elCrown = elCrown.getElementsByTagName('div')[0];

drake.on('drag', function (el) {
    if (document.getElementById('crown')) {
        document.getElementById('crown').outerHTML = "";
    }
});

drake.on('dragend', function (el) {
    var els = $('#right > div').length;

    if(els > 0){
        document.getElementById('right').getElementsByTagName('div')[0].getElementsByTagName('div')[0].prepend(elCrown);
    }

    if (els > 8 || els < 3) {
        document.getElementById('fake-submit').disabled = true;
        document.getElementById('right').style.backgroundColor = "#e0e0e0 ";
    } else {
        document.getElementById('fake-submit').disabled = false;
        document.getElementById('right').style.backgroundColor = "#ffa000";
    }

    if (els > 7) {
        document.getElementById('right').classList.add('full-deck-list');
        document.getElementById('left').classList.add('disabled-dnd');
        /* disable drag and drop for left*/
        var toDisable = document.getElementById('left').getElementsByClassName('card');
        for ( var i = 0; i < toDisable.length; i++) {
            toDisable[i].classList.add('no-dnd');
        }

    } else {
        if (document.getElementsByClassName('full-deck-list').length > 0) {
            document.getElementsByClassName('full-deck-list')[0].classList.remove('full-deck-list');
            document.getElementById('left').classList.remove('disabled-dnd');
        }

        var toDisable = document.getElementById('left').getElementsByClassName('card');
        for ( var i = 0; i < toDisable.length; i++) {
            toDisable[i].classList.remove('no-dnd');
        }
    }
});

function prepareAndSend() {
    var data = [];
    var cards = document.getElementById('right').getElementsByClassName('card');
    var winner = cards[0].getElementsByTagName('div')[0].getElementsByClassName('card-action')[0].getElementsByClassName('deck-id')[0].innerHTML;

    for ( var i = 0; i < cards.length; i++) {
        data[i] = cards[i].getElementsByTagName('div')[0].getElementsByClassName('card-action')[0].getElementsByClassName('deck-id')[0].innerHTML;
    }

    var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", "/addGame");


    /* participantes */
    var hiddenField = document.createElement("select");
    hiddenField.setAttribute("hidden", "hidden");
    hiddenField.setAttribute("type", "select");
    hiddenField.setAttribute("multiple", "multiple");
    hiddenField.setAttribute("name", "players");

    for ( var i = 0; i < data.length; i++) {
        var option = document.createElement("option");
        option.setAttribute("selected", "");
        option.setAttribute("value", data[i]);
        hiddenField.appendChild(option);
    }

    form.appendChild(hiddenField);

    /* gañador */
    hiddenField = document.createElement("input");
    hiddenField.setAttribute("hidden", "hidden");
    hiddenField.setAttribute("type", "number");
    hiddenField.setAttribute("name", "winner");
    hiddenField.setAttribute("value", winner);

    form.appendChild(hiddenField);


    document.body.appendChild(form);
    form.submit();

}

$(document).ready(function(){
    $('.tooltipped').tooltip();
  });