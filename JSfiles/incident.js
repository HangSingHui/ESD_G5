// Simulate that a Sitter has logged in 
var sitter_id = '64199bff455936ecfa302f27'

const session_get_url = "http://127.0.0.1:5004/sitter_all_sessions";
const get_job_url = "http://127.0.0.1:5005/job";
const sitter_rejection_url = "http://127.0.0.1:5200/incident_handling";

var jobs_arr = [];
var status_arr = [];
var jobs_id_arr = [];
var session_id_arr = [];

const fetch_sessions = 
fetch(`${session_get_url}/${sitter_id}`)
.then(response => response.json())
.then(data => {

    if(data.code == 404){
        alert("You have no sessions at all, go find a pet to sit!")
        document.getElementById("1").setAttribute("class", "btn btn-info disabled")
        document.getElementById("2").setAttribute("class", "btn btn-success disabled")
        document.getElementById("3").setAttribute("class", "btn btn-danger disabled")
        
    }

    var temp_job_arr = []
    var curr_sessions = data.data;
    // console.log(curr_sessions);
    for (let index = 0; index < curr_sessions.length; index++) {
        var curr_session = curr_sessions[index];
        // console.log(curr_session);
        var session_id = curr_session["_id"]["$oid"]
        // console.log(session_id);
        var job_id = curr_session["JobID"]["$oid"];
        var status = curr_session["status"];
        // console.log(job_id, status);
        // temp_jobs_status[`${get_job_url}/${job_id}`] = status;
        const fetch_jobs = fetch(`${get_job_url}/${job_id}`)
        .then(response => response.json())
        .then(data => {
        temp_job_arr.push(data.data)
        update_job_arr(temp_job_arr);
        })
    
    
        // jobs_arr.push(`${get_job_url}/${job_id}`)
        status_arr.push(status)
        jobs_id_arr.push(job_id)
        session_id_arr.push(session_id)
    }
    
    updateArr(status_arr, jobs_id_arr, session_id_arr);

    

})

function viewJobs(curr_filter) {
// console.log(jobs_arr, status_arr, jobs_id_arr);
var curr_count = 0 
document.getElementById("job_list").innerHTML = ""
for (let index = 0; index < jobs_arr.length; index++) {
    curr_status = status_arr[index]
    curr_job = jobs_arr[index][0]
    // console.log(curr_status);
    curr_session = session_id_arr[index]
    // console.log(curr_job);
    // console.log(curr_filter);
    curr_id = jobs_id_arr[index]
    
    if (curr_status == curr_filter) {
    curr_count += 1;
    // console.log(curr_job);
    var job_num = `job${index+1}`
    
    var job_title = curr_job["Title"];
    var job_desc = curr_job["Description"];
    var image = curr_job["Image_Path"]
    var start_time = Number(curr_job["Start_datetime"]);
    var end_time = Number(curr_job["End_datetime"]);
    var status = curr_job["Status"]
    var hourly_rate = curr_job["Hourly_rate"]["$numberDecimal"]

    var start_format_date = new Date(start_time).toLocaleDateString("en-US");
    var start_format_time = new Date(start_time).toLocaleTimeString("en-SG");
    var end_format_date = new Date(end_time).toLocaleDateString("en-SG");
    var end_format_time = new Date(end_time).toLocaleTimeString("en-SG");

    // console.log(job_title, job_desc, image, start_format_date, start_format_time, end_format_date, end_format_time, status, hourly_rate);
    var temp_str = 
    `
    <div class="col-4 my-2" id="${curr_id}">
        <div class="card h-100">
        <img src="${image}" class="card-img-top">
        <div class="card-body">
            <h5 class="card-title">${job_title}</h5>
            <p class="card-text">${job_desc}</p>
            <!-- View More Jobs Modal -->
            <button type="button" class="btn btn-info" data-bs-toggle="modal" data-bs-target="#${job_num}Modal">
                View More Info
            </button>
            <!-- Modal -->
            <div class="modal fade" id="${job_num}Modal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                        <h1 class="modal-title fs-5" id="jobModalLabel">${job_title}</h1>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>Job Description: ${job_desc}</p>
                            <p>Starting Date & Time: ${start_format_date} ${start_format_time}</p>
                            <p>Ending Date & Time: ${end_format_date} ${end_format_time}</p>
                            <p>Hourly Rate: $${hourly_rate}/hr</p>
                        </div>
                        <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>`

    if (curr_status == "In-Progress") {
        temp_str += 
        `
        <!-- Cancel Job -->
        <button type="button" class="btn btn-danger" data-bs-toggle="modal" data-bs-target="#cancel${job_num}Modal">
            Cancel Job
        </button>
        <!-- Modal -->
        <div class="modal fade" id="cancel${job_num}Modal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
            <div class="modal-header">
                <h1 class="modal-title fs-5" id="cancelJobModalLabel">Cancel Job?</h1>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                Are you sure you want to cancel this Job? Note that cancellation of this job at this current period will result in a $20 penalty credited from your bank account. Failure to pay the penalty amount will result in your account being locked out.
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-danger" onclick="removeJob('${curr_session}', '${job_num}')" id="job_cancel1">Cancel</button>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Don't Cancel</button>
            </div>
            </div>
        </div>
        </div>
        `
    }
    else if(curr_status == "Completed"){
        temp_str += `<button class="btn btn-success disabled">Completed</button>`
    }
    else{
        temp_str += `<button class="btn btn-danger disabled">Cancelled</button>`
    }

    temp_str +=

    `
        </div>
        </div>
    </div>
    
    `
    // console.log(temp_str);
    document.getElementById("job_list").innerHTML += temp_str
    }
    
    }
    if (curr_count == 0) {
    document.getElementById("job_list").innerHTML = `<h1 class="text-center my-5">No Jobs to View!</h1>`
    }
}


function updateArr(temp_status_arr, temp_job_id_arr, temp_session_id_arr) {
status_arr = temp_status_arr
jobs_id_arr = temp_job_id_arr
session_id_arr = temp_session_id_arr
// console.log(jobidi);
}

function update_job_arr(temp_job_arr) {
jobs_arr = temp_job_arr;
}



function removeJob(session_id, job_num) {
    var myModalEl = document.getElementById(`cancel${job_num}Modal`)
    var modal = bootstrap.Modal.getInstance(myModalEl)
    modal.hide()
    alert("Checking to reject the application, please hold...")
    document.getElementById("reload_div").innerHTML = 
        `
        <h1 class="text-center fw-bold">Updating our database now, please bear with us!</h1>
        <h5 class="text-center fw-bold">In the mean time, here's a cute bear waving, say hi!</h5>
        <img class="d-block mx-auto mb-5" src="https://66.media.tumblr.com/5c059a6fbc4f51e9238a17484f784fcf/tumblr_mvo47boXpt1svecmko1_250.gif">
    `

    const cancel_session = fetch(`${sitter_rejection_url}/${session_id}`,
    {
        method:"PUT",
        headers: {
            "Content-type":"application/json"
        }
    }
    )
    .then(response => response.json())
    .then(data => {
        // console.log(data);
        
        if (data.code==201) {
            document.getElementById("reload_div").innerHTML = 
            `
            <h1 class="text-center fw-bold">Job cancel success!</h1>
            <h5 class="text-center fw-bold mb-5">Redirecting you back to the sessions page...</h5>
            
        `

            setTimeout(function(){
                location.reload(true);
                }, 5000);
        }

        else{
            document.getElementById("reload_div").innerHTML = 
            `
            <h1 class="text-center fw-bold">There was a problem with the cancellation!</h1>
            <h5 class="text-center fw-bold mb-5">Redirecting you back to the sessions page...</h5>
            
        `
        setTimeout(function(){
            location.reload(true);
            }, 5000);
        }
        
        
    })
    .catch(error => {
        console.log(error);
    })
}