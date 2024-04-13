let countWorkoutProgram = 0;

window.addEventListener('load', function () {
    let pace = document.getElementsByClassName('pace');
    let duration = document.getElementsByClassName('duration');
    for (let i = 0; i < pace.length; i++) {
        countWorkoutProgram++;
        pace[i].setAttribute('name', 'pace-'+countWorkoutProgram);
        duration[i].setAttribute('name', 'duration-'+countWorkoutProgram);;
    }
  })

function addWorkoutProgram() {
    countWorkoutProgram++;
    let html = '<div style="margin-top:10px; border-top: 1px solid;" class="workout-program"><div style="margin-top: 10px;">' +
    '<span style="margin-right:5px;">Темп:</span><span><input type="text" name="pace-' + countWorkoutProgram +'" class="vTextField pace">' +
    '</span></div><div style="margin-top: 10px;"><span style="margin-right:5px;">Продолжительность:' +
    '</span><span><input type="number" name="duration-' + countWorkoutProgram +'" class="vIntegerField duration"></span> </div></div>';
    let lastWorkoutProgram = document.querySelectorAll(".workout-program:last-child");
    if(countWorkoutProgram - 1 > 0) {
        lastWorkoutProgram[0].insertAdjacentHTML('afterend', html);
    }
    else {
        document.getElementsByClassName('top-workout-program')[0].insertAdjacentHTML('afterend', html);
    }
}

function deleteWorkoutProgram() {
    let lastWorkoutProgram = document.querySelectorAll(".workout-program:last-child");
    if(countWorkoutProgram > 0) {
        countWorkoutProgram--;
        lastWorkoutProgram[0].remove();
    }
}
