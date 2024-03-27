document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').onsubmit = send_mail;

  // By default, load the inbox
  load_mailbox('inbox');
});


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#single-email-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}


function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Empty previous mailbox
  document.querySelector('#emails-view').innerHTML= '';

  // Get request
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        // Log emails
        console.log(emails)
        // Loop through emails
        for (let i of Object.keys(emails)) {
          // Create div
          const email_div = document.createElement('div');
          email_div.classList.add('email');
          // Mark as read
          if (emails[i].read) {
            email_div.classList.add('is_read');
          }
          // Add subject, sender and timestamp
          email_div.innerHTML = `
              <div>Subject: ${emails[i].subject}</div>
              <div>Sender: ${emails[i].sender}</div>
              <div>Date: ${emails[i].timestamp}</div>
              `;
          // Load single email if clicked
          email_div.addEventListener('click', () => view_mail(emails[i].id));
          // Append email to list
          document.querySelector('#emails-view').append(email_div);
          };
        });
}


function send_mail() {

  // Define variables
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  // Post request
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
    .then(response => response.json())
      .then(result => {
        if ("post" in result) {
            // Load sent box if succesful
            load_mailbox('sent');
        }
        if ("error" in result) {
            // Display the error next to the "To:"
            document.querySelector('#to-text-error-message').innerHTML = result['error']
        }
        });
  return false;
}


function view_mail(id) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'block';

  // Remove previous mail
  document.querySelector('#single-email-view').innerHTML= '';

  // Get email data and display email
  fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {
      // Build email div
      build_email(email);
    });

  // Set the email to read.
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      read: true
    })
  });
}


function build_email(data) {

  // Building blocks email
  const from = document.createElement("div");
  const to = document.createElement("div");
  const subject = document.createElement("div");
  const timestamp = document.createElement("div");
  const reply_button = document.createElement("button");
  const archive_button = document.createElement("button");
  const body = document.createElement("div");

  // Sender, recipient, subject, timestamp and body
  from.innerHTML = `<strong>From: </strong> ${data["sender"]}`;
  to.innerHTML = `<strong>To: </strong> ${data["recipients"].join(", ")}`;
  subject.innerHTML = `<strong>Subject: </strong> ${data["subject"]}`;
  timestamp.innerHTML = `<strong>Timestamp: </strong> ${data["timestamp"]}`;
  body.innerHTML = data["body"];

  // Archive button
  if (data["archived"]) {
    archive_button.innerHTML += "Unarchive";
  } else {
    archive_button.innerHTML += "Archive";
  }
  archive_button.classList = "btn btn-primary btn-new-blue";
  // Add put request to button
  archive_button.addEventListener("click", function() {
    fetch(`/emails/${data["id"]}`, {
      method: 'PUT',
      body: JSON.stringify({
          // Change archived value to opposite of current value
          archived: !data["archived"]
      })
    })
    // Load inbox
    load_mailbox("inbox");
  });

  // Reply button
  reply_button.innerHTML = 'Reply';
  reply_button.classList = "btn btn-primary btn-new-blue"
  reply_button.addEventListener("click", () => compose_reply(data));

  // Append email elements
  document.querySelector("#single-email-view").appendChild(from);
  document.querySelector("#single-email-view").appendChild(to);
  document.querySelector("#single-email-view").appendChild(subject);
  document.querySelector("#single-email-view").appendChild(timestamp);
  document.querySelector("#single-email-view").appendChild(archive_button);
  document.querySelector("#single-email-view").appendChild(reply_button);
  document.querySelector("#single-email-view").appendChild(document.createElement("hr"));
  document.querySelector("#single-email-view").appendChild(body);
}


function compose_reply(data) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#single-email-view').style.display = 'none';

  // Pre-fill composition fields
  document.querySelector('#compose-recipients').value = data["sender"];
  document.querySelector('#compose-subject').value = 'Re: '+data["subject"];
  document.querySelector('#compose-body').value = `\n\n------------------------------------------------\nOn ${data["timestamp"]} ${data["sender"]} wrote:\n "${data["body"]}"`;
}
