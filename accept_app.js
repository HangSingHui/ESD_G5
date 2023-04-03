const get_all_url = "http://localhost:5005/job";
const application_get_url = "http://localhost:5008/application/job";
const sitter_info_url = "http://localhost:5001/sitter"

// Get all sitters

const fetch_sitter = fetch(sitter_info_url)
.then(response => response.json())
.then(data => {
    console.log(data);
})


const response = fetch(get_all_url).then(response => response.json())
.then(data => {
    var jobs = data["data"]
    // console.log(jobs);
    for (let index = 0; index < jobs.length; index++) {
        // console.log(jobs[index]);
        var curr_job = `job${index+1}`

        var job = jobs[index];
        var job_id = jobs[index]["_id"]["$oid"];
        // console.log(job_id);

        var job_title = job["Title"];
        var job_desc = job["Description"];
        var image = job["Image_Path"]
        var start_time = Number(job["Start_datetime"]);
        var end_time = Number(job["End_datetime"]);
        var status = job["Status"]
        var hourly_rate = job["Hourly_rate"]["$numberDecimal"]

        var start_format_date = new Date(start_time).toLocaleDateString("en-US");
        var start_format_time = new Date(start_time).toLocaleTimeString("en-SG");
        var end_format_date = new Date(end_time).toLocaleDateString("en-SG");
        var end_format_time = new Date(end_time).toLocaleTimeString("en-SG");

        // console.log(job_title, job_desc, image, start_format_date, start_format_time, end_format_date, end_format_time, status, hourly_rate);

        var modal_str = 
        `
        <!-- View Job Application Modals -->
        <button class="btn btn-primary btn-sm" data-bs-target="#${curr_job}app" data-bs-toggle="modal" id="${curr_job}all">View Applications</button>
        <div class="modal fade" id="${curr_job}app" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h1 class="modal-title fs-5">Applications</h1>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <ul class="list-group list-group-flush">
        `

        modal_li_str = "";
        modal_info_str = ""

        const app_response = fetch(`${application_get_url}/${job_id}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            applications = data.data;

            for (let app_index = 0; app_index < applications.length; index++) {

                app_ID = applications[app_index]["_id"]["$oid"];
                temp_li = 
                `
                <li class="list-group-item d-flex justify-content-between align-items-center" id="${curr_job}app${app_index+1}" value="${app_ID}">
                    Application ${app_index + 1}
                    <button class="btn btn-primary" data-bs-target="#${curr_job}app${app_index +1}modal" data-bs-toggle="modal">View More</button>
                </li>
                
                `
                // model_li_str += temp_li;
                
            }

            // modal_str += model_li_str;

            

            


        })

        



        if (status == "Open") {
            
            


        }

    }


    if (data.code === 404) {
        console.log("Jobs not found");
    }
    else{
        // console.log(data);
    }
})
.catch(error => {
    console.log(error);
})

// const get_all_job_applications = 

// var test_application_id = '64293aea06864f6b8cac1f3a';
// const accept_application_route = "http://localhost:5100/accept_app";

// fetch(`${accept_application_route}/${test_application_id}`)
// .then(response => response.json())
// .then(data => {
//     console.log(response);
//     if (data.code === 404) {
//         console.log("Application not found");
//     }
//     else{
//         console.log(data);
//     }
// })
// .catch(error => {
//     console.log(error);
// })




window.sessionStorage
let payment_made = sessionStorage.getItem('paid')

if (payment_made != null) {
    var job_id = sessionStorage.getItem('paid')
    var app_id = sessionStorage.getItem('application');
    var view_button = document.getElementById(`${job_id}all`);
    var cancel_button = document.getElementById(`${job_id}cancel`);

    var view_class_arr = view_button.getAttribute('class').split(" ");
    var cancel_class_arr = cancel_button.getAttribute('class').split(" ");

    view_class_arr.push('d-none')
    cancel_class_arr.pop()

    var new_view_class_str = view_class_arr.join(" ")
    var new_cancel_class_str = cancel_class_arr.join(" ")

    view_button.setAttribute('class', new_view_class_str);
    cancel_button.setAttribute('class', new_cancel_class_str);

    var sitter_info = document.getElementById(`${job_id}${app_id}_sitter_info`).innerHTML;
    // console.log(sitter_info);
    document.getElementById(`${job_id}_info`).innerHTML += sitter_info

    const pay_route = "http://localhost:5000/test";
            
    let jsonData = JSON.stringify({
        payment_made : "true"
    })

    fetch(pay_route, {
        method : "POST",
        headers:{
            "Content-type":"application/json"
        },
        body: jsonData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        result = data.data;
        console.log(result);
    })
}

function accept_application(application) {

    var job_app_id = application.id.split("accept")[0];
    var sitter_name = document.getElementById(`${job_app_id}_sitter`).innerText;

    var confirmation = confirm(`Confirm ${sitter_name}'s application?`)
    if (confirmation == true) {
        alert(`You have just accepted ${sitter_name}'s application! Your pet is going to be in good hands :)`)
        var job_id = job_app_id.split("app")[0]
        sessionStorage.setItem('paid','job1');
        sessionStorage.setItem('application', 'app1');
        
        var stripe = Stripe("pk_test_51Ms4GgFrjIdoqzyMIKQv8tYAqcPtO2cm09hNoEoxxnNZC2MlDmmbMYGpmFOHOMXZdJS3u8FI3j8mOjxLdvMHCFeg00I2EsXps1");

        stripe.redirectToCheckout({
            lineItems:[
                {
                    price : 'price_1Ms66XFrjIdoqzyMAsZT14GZ',
                    quantity: 1
                },
            ],
            mode: 'subscription',
            successUrl : "http://127.0.0.1:5500/owner_accept_applications.html",
            cancelUrl : "http://127.0.0.1:5500/owner_accept_applications.html"
        })
        .then(function (){});

        var myModal = document.getElementById(`${job_app_id}modal`);
        var modal = bootstrap.Modal.getInstance(myModal);
        modal.hide()
    }
}

function reject_application(application) {
    job_app_id = application.id.split("reject")[0];
    var myModal = document.getElementById(`${job_app_id}modal`);
    var modal = bootstrap.Modal.getInstance(myModal);
    modal.hide()

    reject_sitter = confirm("Reject sitter?")
    if (reject_sitter == true) {
        var sitter = document.getElementById(`${job_app_id}_sitter`).innerText;
        alert(`You have rejected ${sitter}'s application. We will inform them about the rejection.`)
        myModal.remove()
        document.getElementById(job_app_id).remove()
    }
}

function cancel_sitter(job) {
    cancel_confirm = confirm('Are you sure you want to cancel the current job? You will not receive a full refund on your deposit if you cancel at this time.')
    // var job_id = job.id.split('cancel')[0];
    if (cancel_confirm == true) {
        sessionStorage.clear()
        location.reload()
    }
    
}