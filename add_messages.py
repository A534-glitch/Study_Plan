import os

templates_dir = 'templates'
message_block = '''

<!-- Messages with Auto-Fade -->
{% if messages %}
  {% for message in messages %}
    <div class="auto-fade-message mb-4 p-4 rounded-lg text-center font-medium
      {% if message.tags == 'success' %}bg-green-100 text-green-800
      {% elif message.tags == 'error' %}bg-red-100 text-red-800
      {% elif message.tags == 'warning' %}bg-yellow-100 text-yellow-800
      {% elif message.tags == 'info' %}bg-blue-100 text-blue-800
      {% else %}bg-gray-100 text-gray-800{% endif %}">
      {{ message }}
    </div>
  {% endfor %}
  <script>
    setTimeout(function() {
      document.querySelectorAll('.auto-fade-message').forEach(function(msg) {
        msg.style.transition = 'opacity 1s';
        msg.style.opacity = '0';
        setTimeout(function() { msg.remove(); }, 1000);
      });
    }, 3000);
  </script>
{% endif %}

'''

done = ['base.html', 'admin_manage_users.html', 'admin_dashboard.html', 
        'alumni_products.html', 'alumni_lease_requests.html', 'admin_transactions.html',
        'admin_products.html']

for filename in os.listdir(templates_dir):
    if filename.endswith('.html') and filename not in done:
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'Messages with Auto-Fade' in content:
            print(f'Skipping {filename} - already has')
            continue
        new_content = content.replace('<body>', '<body>' + message_block)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {filename}')

print('Done!')
