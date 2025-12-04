const nextTaskBtn = document.querySelector('.next-task-btn')
const audioId = document.getElementById('audio-id')

nextTaskBtn.addEventListener('click', () => {
    // window.location.href = '/speech_to_text'
    fetch(`/api/v1/tasks/${audioId.value}/unassign`
    , {
        method: 'PATCH'
    }
    ).then(() => {
        window.location.href = '/speech_to_text'
        console.log('Task unassigned')
    }).catch(err => {
        console.log(err)
    })
})