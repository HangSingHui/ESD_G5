const get_all_url = "http://localhost:5005/job"
fetch(get_all_url)
.then(response => response.json())
.then(data => {
    console.log(response);
    if (data.code === 404) {
        console.log("Jobs not found");
    }
    else{
        console.log(data);
    }
})
.catch(error => {
    console.log(error);
})

// const get_all_job_applications = 

var test_application_id = '64293aea06864f6b8cac1f3a';
const accept_application_route = "http://localhost:5100/accept_app";

fetch(`${accept_application_route}/${test_application_id}`)
.then(response => response.json())
.then(data => {
    console.log(response);
    if (data.code === 404) {
        console.log("Application not found");
    }
    else{
        console.log(data);
    }
})
.catch(error => {
    console.log(error);
})




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